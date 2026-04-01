const bcrypt = require('bcrypt');

async function createAdminUser() {
    const password = 'admin123';
    const hashedPassword = await bcrypt.hash(password, 10);
    
    console.log('Password:', password);
    console.log('Hashed password:', hashedPassword);
    
    // Generate SQL
    const sql = `
INSERT INTO users (id, email, hashed_password, role, is_active, tenant_id) 
VALUES (
    gen_random_uuid(),
    'admin@lakshya.com',
    '${hashedPassword}',
    'admin',
    true,
    'default'
) ON CONFLICT (email) DO UPDATE SET
    hashed_password = EXCLUDED.hashed_password;
`;
    
    console.log('\nSQL to update admin user:');
    console.log(sql);
}

createAdminUser().catch(console.error);
