use pyo3::prelude::*;

use crate::ordered_set::{OrderedSet, OrderedSetIterator};

pub mod hash;
pub mod ordered_set;

/// PYTHON_GIL=0
#[pymodule(gil_used = false)]
fn fast_ordset(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<OrderedSet>()?;
    m.add_class::<OrderedSetIterator>()?;
    Ok(())
}
