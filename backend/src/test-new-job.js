const { addParsingJob } = require("./dist/queues/parseQueue");

addParsingJob(
  "d0025aaf-ddbe-4a64-8d02-bfc25fe05b40",
  "uploads/test-resume.txt",
  "txt",
  "test-user",
)
  .then((id) => console.log("Added job:", id))
  .catch((err) => console.error("Error:", err));
