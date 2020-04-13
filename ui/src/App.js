import React from 'react';
import './App.css';

function get_dat() {
  console.log('here')
  fetch('localhost:3001/')
  .then(response => response.json())
  .then((jsonData) => {
    // jsonData is parsed json object received from url
    console.log(jsonData)
  })
  .catch((error) => {
    // handle your errors here
    console.error(error)
  })
}

function App() {
  get_dat()

  return (
    <div className="App">
      <p> hi </p>
    </div>
  );
}

export default App;
