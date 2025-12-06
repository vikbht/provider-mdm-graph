import { useState } from 'react'

function MatchingInterface() {
    const [form, setForm] = useState({
        npi: '', first_name: '', last_name: '', email: '', phone: '', license_number: ''
    })
    const [matches, setMatches] = useState([])
    const [loading, setLoading] = useState(false)

    const handleChange = (e) => {
        setForm({ ...form, [e.target.name]: e.target.value })
    }

    const handleMatch = async (e) => {
        e.preventDefault()
        setLoading(true)
        try {
            const res = await fetch('http://localhost:8000/match', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(form)
            })
            const data = await res.json()
            setMatches(data)
        } catch (e) {
            console.error(e)
        } finally {
            setLoading(false)
        }
    }

    const handleMerge = async (sourceNpi) => {
        if (!confirm('This will merge the source record into the target Golden Record. Continue?')) return

        setLoading(true)
        try {
            const res = await fetch('http://localhost:8000/merge', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    target_npi: form.npi, // Assuming form NPI is the target golden record
                    source_npis: [sourceNpi]
                })
            })
            if (!res.ok) throw new Error('Merge failed')
            alert('Merge Successful! Golden Record updated.')
            setMatches([]) // Clear matches or refresh
        } catch (e) {
            console.error(e)
            alert(e.message)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="card">
            <h2>Match & Deduplication Check</h2>
            <p style={{ color: '#666', fontSize: '0.9rem' }}>Enter provider details to check for existing records. If you are entering a new "Golden" record, put its details here.</p>

            <form onSubmit={handleMatch} style={{ marginTop: '20px' }}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                    <input name="npi" placeholder="Target NPI (Golden)" value={form.npi} onChange={handleChange} />
                    <input name="license_number" placeholder="License Number" value={form.license_number} onChange={handleChange} />
                    <input name="first_name" placeholder="First Name *" required value={form.first_name} onChange={handleChange} />
                    <input name="last_name" placeholder="Last Name *" required value={form.last_name} onChange={handleChange} />
                    <input name="email" placeholder="Email" value={form.email} onChange={handleChange} />
                    <input name="phone" placeholder="Phone" value={form.phone} onChange={handleChange} />
                </div>
                <button type="submit" className="primary" style={{ marginTop: '10px' }} disabled={loading}>
                    {loading ? 'Checking...' : 'Check for Matches'}
                </button>
            </form>

            {matches.length > 0 && (
                <div style={{ marginTop: '30px' }}>
                    <h3>Potential Matches Found ({matches.length})</h3>
                    <div className="results-list">
                        {matches.map((m, idx) => (
                            <div key={idx} className="result-item" style={{
                                borderLeft: `4px solid ${m.match_score > 0.8 ? '#22c55e' : '#eab308'}`,
                                display: 'flex', justifyContent: 'space-between', alignItems: 'center'
                            }}>
                                <div style={{ flex: 1 }}>
                                    <div style={{ display: 'flex', gap: '10px' }}>
                                        <strong>Found NPI: {m.provider2_npi}</strong>
                                        <span style={{ fontWeight: 'bold' }}>{(m.match_score * 100).toFixed(0)}% Match</span>
                                    </div>
                                    <div>Action: {m.recommended_action.toUpperCase()}</div>
                                    <div style={{ fontSize: '0.8rem', color: '#666' }}>Matched on: {m.matching_attributes.join(', ')}</div>
                                </div>
                                {m.recommended_action === 'merge' && (
                                    <button
                                        style={{ background: '#16a34a', color: 'white', border: 'none', padding: '8px 12px', borderRadius: '6px', cursor: 'pointer' }}
                                        onClick={() => handleMerge(m.provider2_npi)}
                                    >
                                        MERGE
                                    </button>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    )
}

export default MatchingInterface
