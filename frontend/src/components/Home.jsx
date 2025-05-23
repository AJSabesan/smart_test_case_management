// src/components/UploadForm.jsx
import { useState } from 'react';
import axios from 'axios';

export default function Home() {
  const [file, setFile] = useState(null);
  const [testCases, setTestCases] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      setLoading(true);
      setError("");
      const response = await axios.post('http://localhost:8000/generate-test-cases/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setTestCases(response.data.test_cases);
    } catch (err) {
      setError(err.response?.data?.error || 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto p-6 bg-white shadow-md rounded-lg mt-10">
      <h1 className="text-2xl font-bold mb-4">SRS Test Case Generator</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="file"
          accept=".pdf"
          onChange={(e) => setFile(e.target.files[0])}
          className="block w-full p-2 border border-gray-300 rounded"
        />
        <button
          type="submit"
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          {loading ? 'Generating...' : 'Upload & Generate'}
        </button>
      </form>

      {error && <p className="mt-4 text-red-600">{error}</p>}

      {testCases.length > 0 && (
        <div className="mt-8">
          <h2 className="text-xl font-semibold mb-4">Generated Test Cases:</h2>
          <ul className="space-y-4">
            {testCases.map((tc) => (
              <li key={tc.id} className="p-4 border border-gray-300 rounded bg-gray-50">
                <p><strong>ID:</strong> {tc.id}</p>
                <p><strong>Description:</strong> {tc.description}</p>
                <p><strong>Expected Result:</strong> {tc.expected_result}</p>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
