// Express 4 doesn't forward rejected promises from async route handlers to
// error-handling middleware automatically - wrap each async handler so a
// thrown/rejected error becomes a 500 instead of an unhandled rejection.
function asyncHandler(fn) {
  return (req, res, next) => Promise.resolve(fn(req, res, next)).catch(next);
}

module.exports = { asyncHandler };
