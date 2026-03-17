
import React from 'react';

const Skills = ({ data }) => {
  return (
    <div className="skills-section">
      <h2>Skills</h2>
      <div className="skills-grid">
        {data.map((item, index) => (
          <div key={index} className="skill-item">
            <h4>{item.name}</h4>
            {item.level && <p><strong>Level:</strong> {item.level}</p>}
            {item.category && <p><strong>Category:</strong> {item.category}</p>}
            {item.years_experience && <p><strong>Years:</strong> {item.years_experience}</p>}
          </div>
        ))}
      </div>
    </div>
  );
};

export default Skills;
