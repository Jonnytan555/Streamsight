import type { FilterOptions } from '../types'

export interface Filters {
  commodity_group: string
  commodity_classification: string
}

interface Props {
  options: FilterOptions | null
  filters: Filters
  onChange: (filters: Filters) => void
}

function FilterBar({ options, filters, onChange }: Props) {
  function set(key: keyof Filters, value: string) {
    onChange({ ...filters, [key]: value })
  }

  const hasActiveFilter = filters.commodity_group || filters.commodity_classification

  return (
    <div className="row g-2 mb-4">
      <div className="col-md-6">
        <select
          className="form-select"
          value={filters.commodity_group}
          onChange={e => set('commodity_group', e.target.value)}
        >
          <option value="">All groups</option>
          {options?.commodity_groups.map(g => (
            <option key={g} value={g}>{g}</option>
          ))}
        </select>
      </div>

      <div className="col-md-6">
        <select
          className="form-select"
          value={filters.commodity_classification}
          onChange={e => set('commodity_classification', e.target.value)}
        >
          <option value="">All classifications</option>
          {options?.commodity_classifications.map(c => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
      </div>

      {hasActiveFilter && (
        <div className="col-12">
          <button
            className="btn btn-sm btn-outline-secondary"
            onClick={() => onChange({ commodity_group: '', commodity_classification: '' })}
          >
            Clear filters
          </button>
        </div>
      )}
    </div>
  )
}

export default FilterBar
