import { useState } from 'react'
import '../App.css'

function SearchInterface({ onSelect }) {
    const [query, setQuery] = useState('')
    const [results, setResults] = useState([])
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)

    const handleSearch = async (e) => {
        e.preventDefault()
        if (!query) return

        setLoading(true)
        setError(null)

        try {
            const response = await fetch(`http://localhost:8000/search?q=${encodeURIComponent(query)}`)
            if (!response.ok) throw new Error('Search failed')

            const data = await response.json()
            setResults(data)
        } catch (err) {
            setError('Failed to fetch results. Ensure backend is running.')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="card">
            <h2>Search Providers</h2>
            <form onSubmit={handleSearch}>
                <input
                    type="text"
                    placeholder="Name, NPI, or Email..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                />
                <button type="submit" className="primary" disabled={loading}>
                    {loading ? 'Searching...' : 'Find Provider'}
                </button>
            </form>

            {error && <div className="error">{error}</div>}

            <div className="results-list" style={{ marginTop: '20px' }}>
                {results.map((p) => (
                    <div key={p.npi} className="result-item" onClick={() => onSelect(p.npi)}>
                        <div style={{ fontWeight: 'bold' }}>{p.first_name} {p.last_name}</div>
                        <div style={{ fontSize: '0.9rem', color: '#666' }}>
                            NPI: {p.npi} | {p.specialties?.[0]?.specialty_name || 'No Specialty'}
                        </div>
                        <div style={{ fontSize: '0.8rem', color: '#888' }}>{p.email}</div>
                    </div>
                ))}
                {results.length === 0 && !loading && <div style={{ textAlign: 'center', color: '#888' }}>No results found</div>}
            </div>
        </div>
    )
}

export default SearchInterface
