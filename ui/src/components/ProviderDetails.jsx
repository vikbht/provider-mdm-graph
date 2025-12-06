import { useState, useEffect } from 'react'

function ProviderDetails({ npi }) {
    const [provider, setProvider] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        async function fetchDetails() {
            setLoading(true)
            try {
                const res = await fetch(`http://localhost:8000/providers/${npi}`)
                const data = await res.json()
                setProvider(data)
            } catch (e) {
                console.error(e)
            } finally {
                setLoading(false)
            }
        }
        if (npi) fetchDetails()
    }, [npi])

    if (loading) return <div className="loading">Loading details...</div>
    if (!provider) return <div className="error">Provider not found</div>

    return (
        <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h2>{provider.first_name} {provider.last_name}, {provider.credentials?.[0]?.license_type || 'MD'}</h2>
                <span style={{
                    background: provider.is_active ? '#dcfce7' : '#fee2e2',
                    color: provider.is_active ? '#166534' : '#991b1b',
                    padding: '4px 8px', borderRadius: '4px', fontSize: '0.8rem'
                }}>
                    {provider.is_active ? 'Active' : 'Inactive'}
                </span>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginTop: '20px' }}>
                <div>
                    <h3>Contact Info</h3>
                    <p><strong>NPI:</strong> {provider.npi}</p>
                    <p><strong>Email:</strong> {provider.email}</p>
                    <p><strong>Phone:</strong> {provider.phone}</p>
                </div>
                <div>
                    <h3>Professional</h3>
                    <p><strong>License:</strong> {provider.credentials?.[0]?.license_number || 'N/A'}</p>
                    <p><strong>Specialty:</strong> {provider.specialties?.[0]?.specialty_name || 'N/A'}</p>
                </div>
            </div>
        </div>
    )
}

export default ProviderDetails
