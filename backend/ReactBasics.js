
import React from 'react';

const Basics = ({ data }) => {
  return (
    <div className="basics-section">
      <h2>Basic Information</h2>
      <div className="basics-grid">
        <div className="field">
          <label>Name:</label>
          <span>{data.name || 'N/A'}</span>
        </div>
        <div className="field">
          <label>Email:</label>
          <span>{data.email || 'N/A'}</span>
        </div>
        <div className="field">
          <label>Phone:</label>
          <span>{data.phone || 'N/A'}</span>
        </div>
        <div className="field">
          <label>Location:</label>
          <span>{data.location || 'N/A'}</span>
        </div>
        {data.summary && (
          <div className="field full-width">
            <label>Summary:</label>
            <p>{data.summary}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Basics;
