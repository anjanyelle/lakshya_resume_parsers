import os

file_path = r"c:\Lalataksha V Company\Main-branch\Lakshya-LLM-Resume-Parser\backend\src\workers\parseWorker.ts"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add crypto import at the top
target_import = 'import { Worker, Job, Processor } from "bullmq";'
replacement_import = 'import { Worker, Job, Processor } from "bullmq";\nimport crypto from "crypto";'

if target_import in content:
    content = content.replace(target_import, replacement_import)
    print("Added crypto import (LF)")
elif target_import.replace("\n", "\r\n") in content:
    content = content.replace(target_import.replace("\n", "\r\n"), replacement_import.replace("\n", "\r\n"))
    print("Added crypto import (CRLF)")
else:
    print("Import target not found")

# 2. Replace updateCandidateWithParsedData body with the email_hash, duplicate detection and status = 'success' updates
target_body = """    const updateQuery = `
      UPDATE candidates 
      SET full_name = COALESCE($1, full_name),
          email = COALESCE($2, email),
          phone = COALESCE($3, phone),
          location = COALESCE($4, location),
          linkedin_url = COALESCE($5, linkedin_url),
          github_url = COALESCE($6, github_url),
          summary = COALESCE($7, summary)${
            hasRawResumeText
              ? `,
          raw_resume_text = COALESCE($8, raw_resume_text)`
              : ""
          },
          updated_at = NOW()
      WHERE id = $${hasRawResumeText ? "9" : "8"}
      RETURNING *
    `;

    // Extract location from locations array or use first location
    const location =
      parsedData.locations && Array.isArray(parsedData.locations)
        ? parsedData.locations[0]
        : null;

    const values = [
      truncateString(parsedData.name || null, 255),
      truncateString(parsedData.email || null, 255),
      truncateString(parsedData.phone || null, 50),
      truncateString(location || null, 255),
      truncateString(parsedData.linkedin || null, 500),
      truncateString(parsedData.github || null, 500),
      truncateString(parsedData.summary || null, 2000), // Summary might be TEXT
    ];

    // Add raw_resume_text if column exists
    if (hasRawResumeText) {
      values.push(null); // raw_resume_text - not stored as a separate field
    }

    values.push(candidateId);"""

replacement_body = """    // Calculate email hash
    const emailHash = parsedData.email
      ? crypto.createHash("md5").update(parsedData.email.trim().toLowerCase()).digest("hex")
      : null;

    // Duplicate Detection logic: check if another parsed candidate has the same email hash
    let reviewStatus = "pending";
    if (emailHash) {
      const duplicateCheck = await client.query(
        "SELECT id FROM candidates WHERE email_hash = $1 AND id != $2 AND status = 'success'",
        [emailHash, candidateId]
      );
      if (duplicateCheck.rows.length > 0) {
        reviewStatus = "duplicate";
        console.log(`[DUPLICATE] Candidate ${candidateId} is a duplicate of candidate ${duplicateCheck.rows[0].id}`);
      }
    }

    const updateQuery = `
      UPDATE candidates 
      SET full_name = COALESCE($1, full_name),
          email = COALESCE($2, email),
          phone = COALESCE($3, phone),
          location = COALESCE($4, location),
          linkedin_url = COALESCE($5, linkedin_url),
          github_url = COALESCE($6, github_url),
          summary = COALESCE($7, summary),
          status = 'success',
          review_status = $8,
          email_hash = COALESCE($9, email_hash)${
            hasRawResumeText
              ? `,
          raw_resume_text = COALESCE($10, raw_resume_text)`
              : ""
          },
          updated_at = NOW()
      WHERE id = $${hasRawResumeText ? "11" : "10"}
      RETURNING *
    `;

    // Extract location from locations array or use first location
    const location =
      parsedData.locations && Array.isArray(parsedData.locations)
        ? parsedData.locations[0]
        : null;

    const values = [
      truncateString(parsedData.name || null, 255),
      truncateString(parsedData.email || null, 255),
      truncateString(parsedData.phone || null, 50),
      truncateString(location || null, 255),
      truncateString(parsedData.linkedin || null, 500),
      truncateString(parsedData.github || null, 500),
      truncateString(parsedData.summary || null, 2000), // Summary might be TEXT
      reviewStatus,
      emailHash,
    ];

    // Add raw_resume_text if column exists
    if (hasRawResumeText) {
      values.push(null); // raw_resume_text - not stored as a separate field
    }

    values.push(candidateId);"""

# Replace body handling LF and CRLF
if target_body in content:
    content = content.replace(target_body, replacement_body)
    print("Replaced update query (LF)")
elif target_body.replace("\n", "\r\n") in content:
    content = content.replace(target_body.replace("\n", "\r\n"), replacement_body.replace("\n", "\r\n"))
    print("Replaced update query (CRLF)")
else:
    print("Update query target not found!")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
