// api/utils/errorHandler.js - Centralized error handling
export const handleApiError = async (response, defaultMessage) => {
  if (!response.ok) {
    const error = await response.text();
    throw new Error(`${defaultMessage}: ${error}`);
  }
};

export const handleFetchError = (error, context = 'API call') => {
  console.error(`${context} failed:`, error);
  throw new Error(`${context} failed: ${error.message}`);
};