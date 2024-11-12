import React, { useState, useRef, useEffect } from 'react';

const DictionaryTable = ({ dictionary, onUpdate }) => {
  // State to keep track of the updated values
  const [updatedValues, setUpdatedValues] = useState({});

  // Handle changes to the input fields
  const handleInputChange = (key, value) => {
    setUpdatedValues(prevState => ({
      ...prevState,
      [key]: value,
    }));
  };

  // Handle submitting new value to update the dictionary
  const handleBlur = (key, value) => {
    if (value !== dictionary[key]) {
      onUpdate(key, value); // Call the update function passed as a prop
    }
  };

  return (
    <div>
      <table border="1">
        <thead>
          <tr>
            <th>Key</th>
            <th>Current Value</th>
            <th>New Value</th>
          </tr>
        </thead>
        <tbody>
          {Object.keys(dictionary).map(key => (
            <tr key={key}>
              <td>{key}</td>
              <td>{dictionary[key]}</td>
              <td>
                <input
                  type="text"
                  value={updatedValues[key] || ''}
                  onChange={(e) => handleInputChange(key, e.target.value)}
                  onBlur={(e) => handleBlur(key, e.target.value)}
                  placeholder="Enter new value"                />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default DictionaryTable;
