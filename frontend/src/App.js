import React, { useState, useEffect } from 'react';
// import logo from './logo.svg';
import './App.css';

function App() {

  const [hello, setHello] = useState(null);
  const [error, setError] = useState(null);
  const [userInfo, setUserInfo] = useState(null);
  const [buttonMessage, setButtonMessage] = useState(null);
  const [buttonCounter, setButtonCounter] = useState(0);

  useEffect(() => {    
    var refreshFailCounter = 0;
    var refreshIntervalId = null;
  
    // Test fetch; will be removed later
    const testFetch = async () => {
      try {
        const response = await fetch('/gui_sync', {
          method: 'POST', 
          headers: {
            'Content-Type': 'application/json', 
          },
          body: JSON.stringify({ command: ['hello'] }), 
        });
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const result = JSON.parse(await response.json());
        setHello(result[0].msg);
        console.log('Test fetch: ', result);
      } catch (err) {
        setError(err.message);
        setHello(err.message);
      }
    }    
    
    const fetchUserInfo = async () => {
      try {
        const response = await fetch('/gui_sync', {
          method: 'POST', 
          headers: {
            'Content-Type': 'application/json', 
          },
          body: JSON.stringify({ command: ['userInfo'] }), 
        });
        if (!response.ok) {
          refreshFailCounter++;
          setUserInfo(`Error #${refreshFailCounter} fetching data`);
          console.log(`Error #${refreshFailCounter} fetching data`);
          if (refreshFailCounter > 10) 
          {
              setUserInfo('Too many errors -- ending attempts to fetch data. Reload page to retry.');
              clearInterval(refreshIntervalId);
          }
          throw new Error('Network response was not ok');
        }
        refreshFailCounter = 0;
        const result = JSON.parse(await response.json());
        console.log('User info fetch: ', result);
        setUserInfo(result);
      } catch (err) {
        setError(err.message);
      }
    }

    // Execute test fetch
    testFetch();

    // Set fetchUserInfo to run periodically
    refreshIntervalId = setInterval(fetchUserInfo, 500);
    // Force first fetch
    fetchUserInfo();

  }, []);

  // Button click handler
  const handleClick = () => {
    setButtonCounter(buttonCounter+1);
    setButtonMessage(`CLICKED ${buttonCounter}X`);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Nexus Control App</h1>
      </header>
      <h1>Generic greeting</h1>
      <p>Hello everyone. Blah.</p>
      <p>Test message from server: {hello}</p>
      <h1>Some controls maybe</h1>
      <button onClick={handleClick}>Click me</button> 
      <p>Button clicked: {buttonMessage}</p>
      <h1>UserInfo</h1>
      <p>{userInfo}</p>
    </div>
  );
}

export default App;
