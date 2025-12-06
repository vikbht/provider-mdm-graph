import { useState } from 'react'
import SearchInterface from './components/SearchInterface'
import ProviderDetails from './components/ProviderDetails'
import MatchingInterface from './components/MatchingInterface'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('search')
  const [selectedNpi, setSelectedNpi] = useState(null)

  const handleProviderSelect = (npi) => {
    setSelectedNpi(npi)
    setActiveTab('details')
  }

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Provider MDM Graph</h1>
        <nav>
          <button
            className={activeTab === 'search' ? 'active' : ''}
            onClick={() => setActiveTab('search')}
          >
            Search
          </button>
          <button
            className={activeTab === 'match' ? 'active' : ''}
            onClick={() => setActiveTab('match')}
          >
            Match & Dedupe
          </button>
          {selectedNpi && (
            <button
              className={activeTab === 'details' ? 'active' : ''}
              onClick={() => setActiveTab('details')}
            >
              Provider Details
            </button>
          )}
        </nav>
      </header>

      <main className="app-content">
        {activeTab === 'search' && (
          <SearchInterface onSelect={handleProviderSelect} />
        )}
        {activeTab === 'details' && selectedNpi && (
          <ProviderDetails npi={selectedNpi} />
        )}
        {activeTab === 'match' && (
          <MatchingInterface />
        )}
      </main>
    </div>
  )
}

export default App
