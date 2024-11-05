import React, { useState, useEffect } from 'react';
import logo from './logo.svg';
import './App.css';

function App() {

  const [hello, setHello] = useState(null);
  const [error, setError] = useState(null);
  const [userInfo, setUserInfo] = useState(null);

  useEffect(() => {    
    var refreshFailCounter = 0;
    var refreshIntervalId = null;
  
    const fetchHello = async () => {
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
        setHello(result[0].a);
        console.log('Got some junk: ', result);
      } catch (err) {
        setError(err.message);
      }
    };
  
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
        setUserInfo(result[0].a);
        // console.log('Got more junk: ', result);
      } catch (err) {
        setError(err.message);
      }
    }

    fetchHello();

    refreshIntervalId = setInterval(fetchUserInfo, 500);
    fetchUserInfo();
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>Generic greeting:</h1>
        <p>Hello everyone. Blah. {hello}</p>
        <h1>UserInfo:</h1>
        <p>{userInfo}</p>
      </header>
    </div>
  );
}

export default App;
