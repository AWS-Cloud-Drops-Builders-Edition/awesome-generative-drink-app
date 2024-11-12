import React, { useState } from 'react'

function App() {
  const [name, setName] = useState('')
  const [greeting, setGreeting] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    const response = await fetch(`${import.meta.env.VITE_API_URL}?name=${encodeURIComponent(name)}`)
    const data = await response.json()
    setGreeting(data.message)
  }

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Enter your name"
        />
        <button type="submit">Get Greeting</button>
      </form>
      {greeting && <p>{greeting}</p>}
    </div>
  )
}

export default App
