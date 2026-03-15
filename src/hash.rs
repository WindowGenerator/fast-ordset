//! Hash and equivalence for Python objects in IndexSet: cached Python hash so Rust Hash is a single write.
//!
//! **GIL cost:** [`Clone`] and [`PartialEq`] for `PyHashable` use [`Python::with_gil`] because they
//! must touch `PyAny` (clone_ref / equality). That is required for correctness with free-threaded
//! Python and is the main cost in set operations that clone or compare keys (e.g. difference,
//! intersection). Use [`PyHashableRef`] for lookups to avoid cloning when you already have a
//! `Bound` and a precomputed hash.
use indexmap::Equivalent;
use pyo3::prelude::*;
use std::hash::{Hash, Hasher};

pub struct PyHashable {
    pub obj: Py<PyAny>,
    hash_val: isize,
}

impl PyHashable {
    /// Build from an unbind'd object and its precomputed Python hash (from `obj.bind(py).hash()?`).
    #[inline]
    pub fn new(obj: Py<PyAny>, hash_val: isize) -> Self {
        Self { obj, hash_val }
    }

    /// Borrow form for lookups: build a key from a precomputed hash and a reference (no clone/unbind).
    #[inline]
    pub fn lookup<'a>(hash_val: isize, obj: &'a Bound<'a, PyAny>) -> PyHashableRef<'a> {
        PyHashableRef { hash_val, obj }
    }

    /// Compare with a `Bound` in Python; used by lookup keys.
    #[inline]
    pub fn eq_bound(&self, other: &Bound<'_, PyAny>, py: Python<'_>) -> bool {
        other.eq(self.obj.bind(py)).unwrap_or(false)
    }
}

/// Borrowed key for lookups (e.g. `__contains__`, `remove`) when you have a `Bound` and don't want to clone.
#[derive(Clone, Copy)]
pub struct PyHashableRef<'a> {
    pub hash_val: isize,
    pub obj: &'a Bound<'a, PyAny>,
}

impl Hash for PyHashableRef<'_> {
    #[inline]
    fn hash<H: Hasher>(&self, state: &mut H) {
        state.write_isize(self.hash_val);
    }
}

impl Equivalent<PyHashable> for PyHashableRef<'_> {
    #[inline]
    fn equivalent(&self, key: &PyHashable) -> bool {
        Python::with_gil(|py| key.eq_bound(self.obj, py))
    }
}

impl Equivalent<PyHashable> for &PyHashable {
    #[inline]
    fn equivalent(&self, key: &PyHashable) -> bool {
        *self == key
    }
}

impl Clone for PyHashable {
    #[inline]
    fn clone(&self) -> Self {
        Self {
            obj: Python::with_gil(|py| self.obj.clone_ref(py)),
            hash_val: self.hash_val,
        }
    }
}

impl Hash for PyHashable {
    #[inline]
    fn hash<H: Hasher>(&self, state: &mut H) {
        state.write_isize(self.hash_val);
    }
}

impl PartialEq for PyHashable {
    #[inline]
    fn eq(&self, other: &Self) -> bool {
        Python::with_gil(|py| self.obj.bind(py).eq(other.obj.bind(py)).unwrap_or(false))
    }
}

impl Eq for PyHashable {}
