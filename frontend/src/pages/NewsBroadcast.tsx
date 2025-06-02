import React, { useState, useEffect, useRef } from 'react';

interface NewsEntry {
  id: string;
  timestamp: string;
  broadcast: string;
  summaries: string[];
}

export default function NewsBroadcast() {
  const [savedBroadcasts, setSavedBroadcasts] = useState<NewsEntry[]>([]);
  const [selectedBroadcast, setSelectedBroadcast] = useState<NewsEntry | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isInitialMount = useRef(true);

  // Load saved broadcasts and selected broadcast ID from local storage on initial render
  useEffect(() => {
    console.log('Attempting to load broadcasts from localStorage...');
    const storedBroadcasts = localStorage.getItem('newsBroadcasts');
    if (storedBroadcasts) {
      try {
        const parsedBroadcasts = JSON.parse(storedBroadcasts);
        console.log('Loaded broadcasts:', parsedBroadcasts);
        setSavedBroadcasts(parsedBroadcasts);

        const storedSelectedId = localStorage.getItem('selectedBroadcastId');
        if (storedSelectedId) {
          console.log('Loaded selected broadcast ID:', storedSelectedId);
          const foundBroadcast = parsedBroadcasts.find((b: NewsEntry) => b.id === storedSelectedId);
          if (foundBroadcast) {
            setSelectedBroadcast(foundBroadcast);
            console.log('Restored selected broadcast:', foundBroadcast);
          } else {
            console.log('Selected broadcast ID found, but broadcast not in loaded data.');
            localStorage.removeItem('selectedBroadcastId'); // Clear invalid ID
          }
        }
      } catch (e) {
        console.error('Error parsing stored broadcasts from localStorage:', e);
        localStorage.removeItem('newsBroadcasts'); // Clear corrupted data
        localStorage.removeItem('selectedBroadcastId');
      }
    } else {
      console.log('No broadcasts found in localStorage.');
    }
  }, []);

  // Save broadcasts to local storage whenever savedBroadcasts changes, but not on initial mount
  useEffect(() => {
    if (isInitialMount.current) {
      isInitialMount.current = false;
      return;
    }
    console.log('Saving broadcasts to localStorage:', savedBroadcasts);
    localStorage.setItem('newsBroadcasts', JSON.stringify(savedBroadcasts));
  }, [savedBroadcasts]);

  // Save selected broadcast ID to local storage whenever selectedBroadcast changes
  useEffect(() => {
    if (selectedBroadcast) {
      localStorage.setItem('selectedBroadcastId', selectedBroadcast.id);
    } else {
      localStorage.removeItem('selectedBroadcastId');
    }
  }, [selectedBroadcast]);

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);

    try {
      const broadcastRes = await fetch('/api/generate_broadcast');
      if (!broadcastRes.ok) {
        throw new Error(`HTTP error! status: ${broadcastRes.status} for broadcast`);
      }
      const broadcastData = await broadcastRes.json();

      const summariesRes = await fetch('/api/summaries');
      if (!summariesRes.ok) {
        throw new Error(`HTTP error! status: ${summariesRes.status} for summaries`);
      }
      const summariesData = await summariesRes.json();

      const newEntry: NewsEntry = {
        id: Date.now().toString(), // Simple unique ID
        timestamp: new Date().toLocaleString(),
        broadcast: broadcastData.broadcast || '',
        summaries: summariesData.summary || [],
      };

      setSavedBroadcasts(prev => [...prev, newEntry]);
      setSelectedBroadcast(newEntry); // Automatically select the newly generated broadcast

    } catch (err: any) {
      console.error("Error generating news content:", err);
      setError(`Failed to generate news content: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = (id: string) => {
    setSavedBroadcasts(prev => prev.filter(entry => entry.id !== id));
    if (selectedBroadcast?.id === id) {
      setSelectedBroadcast(null); // Deselect if the deleted one was selected
    }
  };

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h1 className="text-3xl font-bold mb-4">Objective News Broadcast</h1>

      <button
        onClick={handleGenerate}
        className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded mb-4"
        disabled={loading}
      >
        {loading ? 'Generating...' : 'Generate News Broadcast'}
      </button>

      {error && <p className="text-red-500">{error}</p>}
      {loading && <p>Generating broadcast and summaries...</p>}

      <h2 className="text-2xl font-bold mt-8 mb-4">Saved Broadcasts</h2>
      {savedBroadcasts.length === 0 ? (
        <p>No saved broadcasts. Generate one to get started!</p>
      ) : (
        <div className="space-y-4">
          {savedBroadcasts.map(entry => (
            <div
              key={entry.id}
              className={`p-4 border rounded-lg shadow-sm flex justify-between items-center ${
                selectedBroadcast?.id === entry.id ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
              }`}
            >
              <span className="font-medium">Broadcast from {entry.timestamp}</span>
              <div>
                <button
                  onClick={() => setSelectedBroadcast(entry)}
                  className="bg-green-500 hover:bg-green-700 text-white text-sm py-1 px-3 rounded mr-2"
                >
                  View
                </button>
                <button
                  onClick={() => handleDelete(entry.id)}
                  className="bg-red-500 hover:bg-red-700 text-white text-sm py-1 px-3 rounded"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {selectedBroadcast && (
        <div className="mt-8 p-6 border rounded-lg shadow-lg bg-white">
          <h2 className="text-2xl font-bold mb-4">Broadcast Details ({selectedBroadcast.timestamp})</h2>
          {selectedBroadcast.broadcast ? (
            <p className="whitespace-pre-line text-lg">{selectedBroadcast.broadcast}</p>
          ) : (
            <p>No broadcast text available for this entry.</p>
          )}

          <h3 className="text-xl font-bold mt-8 mb-4">Article Summaries</h3>
          {selectedBroadcast.summaries.length > 0 ? (
            <ul className="list-disc pl-5">
              {selectedBroadcast.summaries.map((summary, index) => (
                <li key={index} className="mb-2">{summary}</li>
              ))}
            </ul>
          ) : (
            <p>No summaries available for this broadcast.</p>
          )}
        </div>
      )}
    </div>
  );
}
