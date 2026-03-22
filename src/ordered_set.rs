use indexmap::IndexSet;
use pyo3::exceptions::{PyIndexError, PyKeyError, PyTypeError};
use pyo3::prelude::*;
use pyo3::types::PyList;
use std::sync::{Mutex, MutexGuard};

use crate::hash::PyHashable;

/// Use Mutex instead of RefCell for this free-GIL (gil_used = false) impl.
#[pyclass]
pub struct OrderedSet {
    inner: Mutex<IndexSet<PyHashable>>,
}

/// Lock the inner set. If the mutex is poisoned (a previous holder panicked), we recover by
/// taking the guard from the poison error and continue; the set may be in an inconsistent
/// state but we avoid propagating the panic.
#[inline]
fn lock_inner(set: &OrderedSet) -> MutexGuard<'_, IndexSet<PyHashable>> {
    set.inner.lock().unwrap_or_else(|e| e.into_inner())
}

#[pymethods]
impl OrderedSet {
    #[new]
    #[pyo3(signature = (initial_items=None))]
    fn __init__(initial_items: Option<&Bound<'_, PyAny>>) -> PyResult<Self> {
        let inner = Mutex::new(match initial_items {
            Some(items) => Self::sequence_to_set(items)?,
            None => IndexSet::new(),
        });
        Ok(OrderedSet { inner })
    }

    #[inline(always)]
    fn __contains__(&self, item: &Bound<'_, PyAny>) -> PyResult<bool> {
        let hash_val = item.hash()?;
        let lookup = PyHashable::lookup(hash_val, item);
        Ok(lock_inner(self).contains(&lookup))
    }

    fn __len__(&self) -> usize {
        lock_inner(self).len()
    }

    fn __repr__(&self, py: Python<'_>) -> PyResult<String> {
        let inner = lock_inner(self);
        let parts: Vec<String> = inner
            .iter()
            .map(|k| k.obj.bind(py).repr()?.extract::<String>())
            .collect::<PyResult<Vec<String>>>()?;
        Ok(format!("OrderedSet([{}])", parts.join(", ")))
    }

    fn __str__(&self, py: Python<'_>) -> PyResult<String> {
        self.__repr__(py)
    }

    fn __eq__(&self, value: &Bound<'_, PyAny>) -> PyResult<bool> {
        let other: Vec<PyHashable> = value
            .try_iter()?
            .map(|item| {
                item.and_then(|elem| {
                    let h = elem.hash()?;
                    Ok(PyHashable::new(elem.unbind(), h))
                })
            })
            .collect::<PyResult<Vec<_>>>()?;
        let inner = lock_inner(self);
        if inner.len() != other.len() {
            return Ok(false);
        }
        for (i, key) in other.iter().enumerate() {
            match inner.get_index(i) {
                Some(k) if k == key => {}
                _ => return Ok(false),
            }
        }
        Ok(true)
    }

    fn __getitem__<'a>(&self, index: &Bound<'a, PyAny>) -> PyResult<Bound<'a, PyAny>> {
        let py = index.py();
        let index_val = index
            .extract::<isize>()
            .map_err(|_| PyTypeError::new_err("OrderedSet indices must be integers"))?;
        let inner = lock_inner(self);
        let idx = Self::resolve_index(inner.len(), index_val)
            .ok_or_else(|| PyIndexError::new_err("index out of range"))?;
        let elem = inner
            .get_index(idx)
            .map(|k| k.obj.clone_ref(py))
            .ok_or_else(|| PyIndexError::new_err("index out of range"))?;
        Ok(elem.bind(py).clone())
    }

    fn __iter__(slf: PyRef<'_, Self>) -> OrderedSetIterator {
        let py = slf.py();
        // SAFETY: We create a new Py<OrderedSet> that owns a strong reference to the same
        // object. The iterator holds this owned reference, so the set stays alive for the
        // iterator's lifetime and the pointer remains valid.
        OrderedSetIterator {
            set: unsafe { Py::from_borrowed_ptr(py, slf.as_ptr()) },
            index: 0,
        }
    }

    fn add(&self, item: &Bound<'_, PyAny>) -> PyResult<()> {
        let hash_val = item.hash()?;
        let key = PyHashable::new(item.clone().unbind(), hash_val);
        lock_inner(self).insert(key);
        Ok(())
    }

    fn remove(&self, item: &Bound<'_, PyAny>) -> PyResult<()> {
        let hash_val = item.hash()?;
        let lookup = PyHashable::lookup(hash_val, item);
        let removed = lock_inner(self).shift_remove(&lookup);
        if removed {
            Ok(())
        } else {
            Err(PyKeyError::new_err(item.repr()?.extract::<String>()?))
        }
    }

    #[pyo3(signature = (index = -1))]
    fn pop<'a>(&self, py: Python<'a>, index: isize) -> PyResult<Bound<'a, PyAny>> {
        let mut inner = lock_inner(self);
        let len = inner.len();
        if len == 0 {
            return Err(PyKeyError::new_err("pop from an empty set"));
        }
        let idx = Self::resolve_index(len, index)
            .ok_or_else(|| PyIndexError::new_err("pop index out of range"))?;
        let elem = inner
            .get_index(idx)
            .map(|k| k.obj.clone_ref(py))
            .ok_or_else(|| PyIndexError::new_err("pop index out of range"))?;
        inner.shift_remove_index(idx);
        Ok(elem.bind(py).clone())
    }

    fn clear(&self) {
        lock_inner(self).clear();
    }

    fn copy(&self) -> Self {
        OrderedSet {
            inner: Mutex::new(lock_inner(self).clone()),
        }
    }

    fn to_list<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyList>> {
        let inner = lock_inner(self);
        let items: Vec<Bound<'py, PyAny>> = inner
            .iter()
            .map(|k| k.obj.clone_ref(py).bind(py).clone())
            .collect();
        PyList::new(py, items)
    }

    fn update(&self, items: &Bound<'_, PyAny>) -> PyResult<()> {
        let iter = items.try_iter()?;
        let mut inner = lock_inner(self);
        let (lower, upper) = iter.size_hint();
        inner.reserve(upper.unwrap_or(lower));
        for item in iter {
            let elem = item?;
            let hash_val = elem.hash()?;
            inner.insert(PyHashable::new(elem.unbind(), hash_val));
        }
        Ok(())
    }

    fn union(&self, items: &Bound<'_, PyAny>) -> PyResult<Self> {
        let other = self.other_as_index_set(items)?;
        let mut new_inner = lock_inner(self).clone();
        new_inner.reserve(other.len());
        new_inner.extend(other);
        Ok(OrderedSet {
            inner: Mutex::new(new_inner),
        })
    }

    fn difference(&self, other_items: &Bound<'_, PyAny>) -> PyResult<Self> {
        let other_set = self.other_as_index_set(other_items)?;
        let inner = lock_inner(self);
        let mut new_inner = IndexSet::with_capacity(inner.len());
        for k in inner.iter().filter(|k| !other_set.contains(k)) {
            new_inner.insert(k.clone());
        }
        Ok(OrderedSet {
            inner: Mutex::new(new_inner),
        })
    }

    fn difference_update(&self, other_items: &Bound<'_, PyAny>) -> PyResult<()> {
        let other_set = self.other_as_index_set(other_items)?;
        let new_inner = {
            let inner = lock_inner(self);
            inner
                .iter()
                .filter(|k| !other_set.contains(k))
                .cloned()
                .collect::<IndexSet<_>>()
        };
        *lock_inner(self) = new_inner;
        Ok(())
    }

    fn symmetric_difference(&self, other_items: &Bound<'_, PyAny>) -> PyResult<Self> {
        let other_set = self.other_as_index_set(other_items)?;
        let inner = lock_inner(self);
        let cap = inner.len() + other_set.len();
        let mut new_inner = IndexSet::with_capacity(cap);
        for k in inner.symmetric_difference(&other_set) {
            new_inner.insert(k.clone());
        }
        Ok(OrderedSet {
            inner: Mutex::new(new_inner),
        })
    }

    fn symmetric_difference_update(&self, other_items: &Bound<'_, PyAny>) -> PyResult<()> {
        let other_set = self.other_as_index_set(other_items)?;
        let (self_minus_other, other_minus_self) = {
            let inner = lock_inner(self);
            let self_minus_other: IndexSet<PyHashable> =
                inner.difference(&other_set).cloned().collect();
            let mut other_minus_self = Vec::with_capacity(other_set.len());
            for k in other_set.iter() {
                if !inner.contains(k) {
                    other_minus_self.push(k.clone());
                }
            }
            (self_minus_other, other_minus_self)
        };
        let mut inner = lock_inner(self);
        *inner = self_minus_other;
        inner.reserve(other_minus_self.len());
        for k in other_minus_self {
            inner.insert(k);
        }
        Ok(())
    }

    fn intersection(&self, other_items: &Bound<'_, PyAny>) -> PyResult<Self> {
        let other_set = self.other_as_index_set(other_items)?;
        let inner = lock_inner(self);
        let cap = inner.len().min(other_set.len());
        let mut new_inner = IndexSet::with_capacity(cap);
        for k in inner.intersection(&other_set) {
            new_inner.insert(k.clone());
        }
        Ok(OrderedSet {
            inner: Mutex::new(new_inner),
        })
    }

    fn intersection_update(&self, other_items: &Bound<'_, PyAny>) -> PyResult<()> {
        let other_set = self.other_as_index_set(other_items)?;
        let new_inner = {
            let inner = lock_inner(self);
            inner
                .intersection(&other_set)
                .cloned()
                .collect::<IndexSet<_>>()
        };
        *lock_inner(self) = new_inner;
        Ok(())
    }

    fn __or__(&self, other_items: &Bound<'_, PyAny>) -> PyResult<Self> {
        self.union(other_items)
    }

    fn __ior__(&self, other_items: &Bound<'_, PyAny>) -> PyResult<()> {
        self.update(other_items)
    }

    fn __xor__(&self, other_items: &Bound<'_, PyAny>) -> PyResult<Self> {
        self.symmetric_difference(other_items)
    }

    fn __ixor__(&self, other_items: &Bound<'_, PyAny>) -> PyResult<()> {
        self.symmetric_difference_update(other_items)
    }

    fn __sub__(&self, other_items: &Bound<'_, PyAny>) -> PyResult<Self> {
        self.difference(other_items)
    }

    fn __isub__(&self, other_items: &Bound<'_, PyAny>) -> PyResult<()> {
        self.difference_update(other_items)
    }

    fn __and__(&self, other_items: &Bound<'_, PyAny>) -> PyResult<Self> {
        self.intersection(other_items)
    }

    fn __iand__(&self, other_items: &Bound<'_, PyAny>) -> PyResult<()> {
        self.intersection_update(other_items)
    }
}

impl OrderedSet {
    /// Resolve a Python-style index (supports negative) to a `usize`, or `None` if out of range.
    fn resolve_index(len: usize, index: isize) -> Option<usize> {
        if len == 0 {
            return None;
        }
        let mut i = index;
        if i < 0 {
            i += len as isize;
        }
        if i < 0 || (i as usize) >= len {
            None
        } else {
            Some(i as usize)
        }
    }

    fn sequence_to_set(seq: &Bound<'_, PyAny>) -> PyResult<IndexSet<PyHashable>> {
        let iter = seq.try_iter()?;
        let (lower, upper) = iter.size_hint();
        let mut set = IndexSet::with_capacity(upper.unwrap_or(lower));
        for item in iter {
            let elem = item?;
            let hash_val = elem.hash()?;
            set.insert(PyHashable::new(elem.unbind(), hash_val));
        }
        Ok(set)
    }

    fn other_as_index_set(&self, other: &Bound<'_, PyAny>) -> PyResult<IndexSet<PyHashable>> {
        if let Ok(other_ordered) = other.downcast::<OrderedSet>() {
            let other_ref = other_ordered.try_borrow()?;
            return Ok(lock_inner(&other_ref).clone());
        }
        Self::sequence_to_set(other)
    }
}

/// Iterator over an OrderedSet. Does not snapshot the set: if the set is mutated
/// (by this or another thread) during iteration, elements may be skipped or
/// duplicated, or iteration may stop early. Same as Python's dict/set iteration semantics.
#[pyclass]
pub struct OrderedSetIterator {
    set: Py<OrderedSet>,
    index: usize,
}

#[pymethods]
impl OrderedSetIterator {
    fn __iter__(slf: PyRef<'_, Self>) -> PyRef<'_, Self> {
        slf
    }

    fn __next__<'py>(mut slf: PyRefMut<'py, Self>, py: Python<'py>) -> Option<Bound<'py, PyAny>> {
        let result = {
            let set_ref = unsafe { slf.set.bind(py).downcast_unchecked::<OrderedSet>() };
            let set_guard = set_ref.try_borrow().ok()?;
            let inner = lock_inner(&set_guard);
            let elem_ref = inner.get_index(slf.index)?;
            let bound_elem = elem_ref.obj.clone_ref(py).bind(py).clone();
            Some(bound_elem)
        };
        if result.is_some() {
            slf.index += 1;
        }
        result
    }
}
