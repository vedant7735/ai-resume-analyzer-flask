import React, { useState, useMemo } from 'react';
import { Country, City } from 'country-state-city';
import './JobFilters.css';

const SearchIcon = ({ size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="11" cy="11" r="6" stroke="currentColor" strokeWidth="2" />
    <path d="M20 20L16.65 16.65" stroke="currentColor" strokeWidth="2" />
  </svg>
);

export default function JobFilters({ filters, setFilters, onSearch, loading, isCollapsed, setIsCollapsed, analysisData }) {
  const [locInput, setLocInput] = useState('');

  const getPrediction = (input, list) => {
    if (!input.trim()) return '';
    const match = list.find(item => item.toLowerCase().startsWith(input.toLowerCase()));
    return match ? input + match.slice(input.length) : '';
  };

  // Memoize the base country list
  const GLOBAL_COUNTRIES = useMemo(() => {
    const base = ['Remote', 'Worldwide', 'Europe', 'Asia', 'North America'];
    const countries = Array.from(new Set(Country.getAllCountries().map(c => c.name)));
    return [...base, ...countries];
  }, []);

  // Dynamically determine available locations based on selected pills
  const availableLocations = useMemo(() => {
    // Find if any of the selected locations are valid countries
    const selectedCountries = Country.getAllCountries().filter(c =>
      filters.locations.includes(c.name)
    );

    if (selectedCountries.length > 0) {
      // If countries are selected, suggest cities within those countries
      let cities = [];
      selectedCountries.forEach(c => {
        cities = cities.concat(City.getCitiesOfCountry(c.isoCode).map(city => city.name));
      });
      return Array.from(new Set(cities));
    }

    // Otherwise, suggest countries
    return GLOBAL_COUNTRIES;
  }, [filters.locations, GLOBAL_COUNTRIES]);

  const locPrediction = getPrediction(locInput, availableLocations);

  const handleAddLocation = (e) => {
    if (e.key === 'Enter' || e.key === 'Tab') {
      if (locPrediction) {
        e.preventDefault();
        if (!filters.locations.includes(locPrediction)) {
          setFilters({ ...filters, locations: [...filters.locations, locPrediction] });
        }
        setLocInput('');
      } else if (e.key === 'Enter' && locInput.trim()) {
        e.preventDefault();
        if (!filters.locations.includes(locInput.trim())) {
          setFilters({ ...filters, locations: [...filters.locations, locInput.trim()] });
        }
        setLocInput('');
      }
    }
  };

  const handleRemoveLocation = (loc) => {
    setFilters({ ...filters, locations: filters.locations.filter(l => l !== loc) });
  };

  const toggleWorkMode = (mode) => {
    const isSelected = filters.workModes.includes(mode);
    let newModes = isSelected
      ? filters.workModes.filter(m => m !== mode)
      : [...filters.workModes, mode];
    setFilters({ ...filters, workModes: newModes });
  };

  const handleSalaryChange = (field, value) => {
    const numericValue = value.replace(/[^0-9]/g, '');
    setFilters({ ...filters, [field]: numericValue });
  };

  if (isCollapsed) {
    // Generate summary text
    const parts = [];
    if (filters.workModes?.length > 0) parts.push(filters.workModes.map(m => m.toUpperCase()).join('/'));

    let salaryStr = '';
    if (filters.salaryMin && filters.salaryMax) salaryStr = `${filters.salaryMin}-${filters.salaryMax}LPA`;
    else if (filters.salaryMin) salaryStr = `>${filters.salaryMin}LPA`;
    else if (filters.salaryMax) salaryStr = `<${filters.salaryMax}LPA`;
    if (salaryStr) parts.push(salaryStr);

    if (filters.locations.length > 0) parts.push(filters.locations.map(l => l.toUpperCase()).join(', '));

    return (
      <div className="job-filters-container collapsed">
        <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>SEARCH FILTERS</span>
        <span className="summary-bullet">•</span>
        <div className="filters-summary">
          {parts.length > 0 ? parts.join(' • ') : 'NO FILTERS APPLIED'}
        </div>
        <button className="summary-edit-btn" onClick={() => setIsCollapsed(false)}>
          Edit Search
        </button>
      </div>
    );
  }

  return (
    <div className="job-filters-container">
      <div className="filter-group">
        <span className="filter-label">LOCATION</span>
        <div className="pill-container">
          {filters.locations.map(loc => (
            <div key={loc} className="filter-pill" onClick={() => handleRemoveLocation(loc)}>
              {loc} <span className="pill-remove">×</span>
            </div>
          ))}
          <div className="add-pill-input-wrapper">
            {!locInput && <span className="ghost-text">+ Add Location</span>}
            {locPrediction && <span className="ghost-text" style={{ opacity: 0.3 }}>{locPrediction}</span>}
            <input
              type="text"
              className="add-pill-input"
              value={locInput}
              onChange={(e) => setLocInput(e.target.value)}
              onKeyDown={handleAddLocation}
            />
          </div>
        </div>
      </div>

      <div className="filter-group">
        <span className="filter-label">WORK MODE</span>
        <div className="pill-container">
          {['Remote', 'Hybrid', 'Onsite'].map(mode => (
            <div
              key={mode}
              className={`filter-pill ${filters.workModes.includes(mode) ? 'active' : ''}`}
              onClick={() => toggleWorkMode(mode)}
            >
              {filters.workModes.includes(mode) && '✓ '} {mode}
            </div>
          ))}
        </div>
      </div>

      <div className="filter-group">
        <span className="filter-label">SALARY RANGE</span>
        <span className="filter-sublabel">Filter by approx. LPA equivalent (all currencies converted)</span>
        <div className="salary-inputs">
          <div className="salary-input-group">
            <span className="salary-prefix">MIN:</span>
            <input
              type="text"
              className="salary-input"
              placeholder="0"
              value={filters.salaryMin}
              onChange={(e) => handleSalaryChange('salaryMin', e.target.value)}
            />
            <span className="salary-suffix">LPA</span>
          </div>
          <div className="salary-input-group">
            <span className="salary-prefix">MAX:</span>
            <input
              type="text"
              className="salary-input"
              placeholder="--"
              value={filters.salaryMax}
              onChange={(e) => handleSalaryChange('salaryMax', e.target.value)}
            />
            <span className="salary-suffix">LPA</span>
          </div>
        </div>
      </div>

      <div className="filters-actions">
        <button className="btn-search" onClick={onSearch} disabled={loading}>
          <SearchIcon size={18} />
          {loading ? 'Searching live jobs...' : 'Find Jobs'}
        </button>
      </div>
    </div>
  );
}
