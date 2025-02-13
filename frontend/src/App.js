import React, { useState, useRef, useEffect } from 'react';
// import logo from './logo.svg';
import './App.css';
import DictionaryTable from './DictionaryTable';


function App() {

  // State: variables whose state changes cause app re-render
  const [appStatusMessage, setAppStatusMessage] = useState('');
  const [config, setConfig] = useState('Waiting...');
  const [telemetry, setTelemetry] = useState('Waiting...');

  // Refs: variables whose state is preserved across re-renders
  const activeUser = useRef({ 'id' : 'none', 'name' : 'none'});
  const refreshIntervalId = useRef(null);
  const refreshFailCounter = useRef(0);
  const testButtonCounter = useRef(0);

  // Test if an object is empty (this is not built into Javascript...)
  function isEmpty(obj) {
    return Object.keys(obj).length === 0;
  }

  // Get the list of users
  const fetchUserList = () => {
    return new Promise((resolve, reject) => {
      fetch('/admin_sync', {
        method: 'POST', 
        headers: {
          'Content-Type': 'application/json', 
        },
        body: JSON.stringify({ command: ['get_active_user_list'] }), 
      })
      .then(response => {
        if (!response.ok) {
          return Promise.reject(new Error('get_active_user_list: Network response was not ok'));
        }
        return response.json();  // returns a promise
      })
      .then(responseJson => {
        const users = JSON.parse(responseJson);
        console.log('User list: ', users);
        for (const user of users) {
          // console.log(`User ${user.id} ${user.name}`);
          if (activeUser.current.id == 'none') {
            activeUser.current = JSON.parse(JSON.stringify(user));  // cheesy way to make a copy of the user object
            console.log(`SET Active user: ${activeUser.current.id}`);
          }
        }
        resolve(users);  // resolve the promise with the user list
      })
      .catch(err => {
        setAppStatusMessage(err.message);  // handle error
        reject(err);  // reject the promise with the error
      });
    });
  };
  
  // Get config information
  const fetchConfigInfo = () => {
    return new Promise((resolve, reject) => {
      // console.log(`CONFIG Active user: ${activeUser.current.id}`);
      fetch('/admin_sync', {
        method: 'POST', 
        headers: {
          'Content-Type': 'application/json', 
        },
        body: JSON.stringify({ command: ['get_config', activeUser.current.id] }), 
      })
      .then(response => {
        if (!response.ok) {
          return Promise.reject(new Error('get_config: Network response was not ok'));
        }
        return response.json();  // returns a promise
      })
      .then(responseJson => {
        const config = JSON.parse(responseJson);
        console.log('Get config: ', config);
        if (isEmpty(config)) {
          setConfig('Empty...');
        } else {
          setConfig(config);
        }
        resolve(config);  // resolve the promise with the config result
      })
      .catch(err => {
        setAppStatusMessage(err.message);  // handle error
        reject(err);  // reject the promise with the error
      });
    });
  };

  const handleConfigUpdate = (key, newValue) => {
    setConfig(prevConfig => ({
      ...prevConfig,
      [key]: newValue,
    }));
  };
  
  // Push config button click handler
  const handlePushConfigClick = async () => {
    try {
      const response = await fetch('/admin_sync', {
        method: 'POST', 
        headers: {
          'Content-Type': 'application/json', 
        },
        body: JSON.stringify({ command: ['set_config', activeUser.current.id, JSON.stringify(config)]}), 
      });
      if (!response.ok) {
        throw new Error('set_config: Network response was not ok');
      }
      const result = JSON.parse(await response.json());
    } catch (err) {
      setAppStatusMessage(err.message);
    }};

  // Start logging button click handler
  const handleStartLoggingClick = async () => {
    try {
      const response = await fetch('/admin_sync', {
        method: 'POST', 
        headers: {
          'Content-Type': 'application/json', 
        },
        body: JSON.stringify({ command: ['start_logging', activeUser.current.id]}), 
      });
      if (!response.ok) {
        throw new Error('start_logging: Network response was not ok');
      }
      const result = JSON.parse(await response.json());
    } catch (err) {
      setAppStatusMessage(err.message);
    }};

  // Stop logging button click handler
  const handleStopLoggingClick = async () => {
    try {
      const response = await fetch('/admin_sync', {
        method: 'POST', 
        headers: {
          'Content-Type': 'application/json', 
        },
        body: JSON.stringify({ command: ['stop_logging', activeUser.current.id]}), 
      });
      if (!response.ok) {
        throw new Error('stop_logging: Network response was not ok');
      }
      const result = JSON.parse(await response.json());
    } catch (err) {
      setAppStatusMessage(err.message);
    }};
  
  // Get telemetry for the active user 
  const fetchTelemetry = () => {
    fetch('/admin_sync', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ command: ['get_telemetry', activeUser.current.id] }),
    })
    .then(response => {
      if (!response.ok) {
        // Handle the error
        refreshFailCounter.current = refreshFailCounter.current + 1;
        setTelemetry(`Error #${refreshFailCounter.current} fetching data`);
        console.log(`Error #${refreshFailCounter.current} fetching data`);
        if (refreshFailCounter.current > 9) {
          setTelemetry('Too many errors -- ending attempts to fetch data.');
          clearInterval(refreshIntervalId.current);
        }
        return Promise.reject(new Error('get_telemetry: Network response was not ok')); // Reject the promise
      }
      return response.json(); // Return the parsed JSON (a promise)
    })
    .then(result => {
      refreshFailCounter.current = 0;
      //console.log('Telemetry fetch: ', result);
      if (isEmpty(result)) {
        setTelemetry('Empty...');
      } else {
        setTelemetry(result);
      }
    })
    .catch(err => {
      // Handle errors here
      setAppStatusMessage(err.message);
    });
  };

  // Executes upon every render. Sometimes twice (in dev mode). 
  useEffect(() => {    
    // Once fetchUserList completes, fetchConfigInfo is called, then 
    // set up the telemetry interval
    fetchUserList()
    .then(users => {
      return fetchConfigInfo(); 
    })
    .then(result => {
      // Set an interval to run fetchUserInfo periodically
      if (refreshIntervalId.current == null)
        {
          refreshIntervalId.current = setInterval(fetchTelemetry, 500);
          console.log('SET UP INTERVAL');
        }  
    })
    .catch(error => {
      console.error('An error occurred:', error);
    });
  }, []); 
  // The list at the end of useEffect contains dependencies. 
  // Only re-run useEffect upon re-render if a dependency has changed.
  // Empty list means never re-run it. Missing list means always re-run it.

  return (
    <div className="App">
      <header className="App-header">
        <h1>Nexus Admin App</h1>
      </header>
      <h2>Active User Session</h2>
      <h3>ID: {activeUser.current.id} | Name: {activeUser.current.name}</h3>
      <p>If no user shown, ensure Nexus and VR are running then reload.</p>
      <p>NOTE: Current version of app only controls first active user returned by Nexus.</p>

      <h2>User Session Config</h2>
      <center>
      <DictionaryTable dictionary={config} onUpdate={handleConfigUpdate} />
      </center>
      <button onClick={handlePushConfigClick}>Push Updated Config</button> 

      <h2>User Session Logging</h2>
      <button onClick={handleStartLoggingClick}>Start Logging</button> 
      <button onClick={handleStopLoggingClick}>Stop Logging</button> 

      <h2>User Session Telemetry</h2>
      <p>{telemetry}</p>
      If no telemetry shown, ensure Nexus and VR are running then reload.

      <h3>--------------------------------------------</h3>
      <h3>app status message</h3>
      <p>{appStatusMessage}</p>
    </div>
  );
}

export default App;
