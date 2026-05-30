const { Pool } = require('./node_modules/pg');
const pool = new Pool({ host: 'localhost', port: 5432, database: 'resume_parser', user: 'postgres', password: 'Surya@123' });
pool.connect().then(function(client) {
  return client.query("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name").then(function(r) { 
    console.log('Tables:', r.rows.map(function(x){ return x.table_name; }).join(', ')); 
    return client.query("SELECT column_name FROM information_schema.columns WHERE table_name = 'candidates' ORDER BY ordinal_position");
  }).then(function(r) {
    console.log('Candidates columns:', r.rows.map(function(x){ return x.column_name; }).join(', ')); 
    client.release(); 
    pool.end(); 
  }).catch(function(e) { 
    console.error('Error:', e.message); client.release(); pool.end(); 
  });
}).catch(function(e) { console.error('Connect error:', e.message); pool.end(); });
