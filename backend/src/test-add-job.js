const { addParsingJob } = require("./dist/queues/parseQueue");

addParsingJob(
  "22275da3-3748-45e5-a903-1a5011941663",
  "uploads/test-resume.txt",
  "txt",
  "test-user",
)
  .then((id) => console.log("Added job:", id))
  .catch((err) => console.error("Error:", err));
