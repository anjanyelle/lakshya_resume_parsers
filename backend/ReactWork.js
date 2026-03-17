
import React from 'react';

const WorkExperience = ({ data }) => {
  return (
    <div className="work-section">
      <h2>Work Experience</h2>
      <div className="work-list">
        {data.map((item, index) => (
          <div key={index} className="work-item">
            <h3>{item.title}</h3>
            <p className="subtitle">
              {item.company} {item.location && `• ${item.location}`}
            </p>
            <p className="dates">
              {item.startDate} - {item.endDate || (item.current ? 'Present' : 'N/A')}
              {item.current && <span className="current-badge">Current</span>}
            </p>
            {item.description && (
              <div className="description">{item.description}</div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default WorkExperience;
