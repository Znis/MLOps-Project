import { useState, useRef } from 'react';
import { Link } from 'react-router-dom';
import api from '@/api';

const PDF_MIME = 'application/pdf';
const PDF_EXT = '.pdf';

function IndexPage() {
  const [file, setFile] = useState(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [uploading, setUploading] = useState(false);
  const inputRef = useRef(null);

  function isPdf(f) {
    if (!f) return false;
    const okType = f.type === PDF_MIME;
    const name = (f.name || '').toLowerCase();
    const okExt = name.endsWith(PDF_EXT);
    return okType || okExt;
  }

  function handleFileChange(e) {
    const chosen = e.target.files?.[0];
    setError('');
    setSuccess('');
    if (!chosen) {
      setFile(null);
      return;
    }
    if (!isPdf(chosen)) {
      setError('Please select a PDF file only.');
      setFile(null);
      e.target.value = '';
      return;
    }
    setFile(chosen);
  }

  function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    setError('');
    setSuccess('');
    const dropped = e.dataTransfer?.files?.[0];
    if (!dropped) return;
    if (!isPdf(dropped)) {
      setError('Please use a PDF file only.');
      return;
    }
    setFile(dropped);
    if (inputRef.current) inputRef.current.value = '';
  }

  function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setSuccess('');
    if (!file) {
      setError('Please select a PDF file first.');
      return;
    }
    setUploading(true);
    try {
      await api.uploadDocument(file);
      setSuccess('Document uploaded successfully.');
      setFile(null);
      if (inputRef.current) inputRef.current.value = '';
    } catch (err) {
      const msg = err?.data?.message || err?.message || 'Upload failed.';
      setError(msg);
    } finally {
      setUploading(false);
    }
  }

  function clearFile() {
    setFile(null);
    setError('');
    setSuccess('');
    if (inputRef.current) inputRef.current.value = '';
  }

  return (
    <div className="flex flex-col grow w-full max-w-xl mx-auto pt-8 pb-12">
      <div className="font-urbanist space-y-1 mb-8">
        <h1 className="text-2xl font-semibold text-main-text">Upload document</h1>
        <p className="text-primary-blue/90 text-sm">PDF only. Your file is sent to the backend when you submit.</p>
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col gap-6">
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          className={`
            relative border-2 border-dashed rounded-2xl p-10 text-center transition-colors
            ${file ? 'border-primary-blue bg-primary-blue/10' : 'border-primary-blue/50 bg-primary-blue/5 hover:bg-primary-blue/10'}
          `}
        >
          <input
            ref={inputRef}
            type="file"
            accept=".pdf,application/pdf"
            onChange={handleFileChange}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            aria-label="Choose PDF file"
          />
          {file ? (
            <div className="pointer-events-none flex flex-col items-center gap-2">
              <span className="text-4xl" aria-hidden>📄</span>
              <p className="font-urbanist font-medium text-main-text">{file.name}</p>
              <p className="text-sm text-primary-blue/80">{(file.size / 1024).toFixed(1)} KB</p>
            </div>
          ) : (
            <div className="pointer-events-none flex flex-col items-center gap-2">
              <span className="text-4xl" aria-hidden>📁</span>
              <p className="font-urbanist font-medium text-main-text">Drop a PDF here or click to browse</p>
              <p className="text-sm text-primary-blue/80">Only .pdf files are accepted</p>
            </div>
          )}
        </div>

        {file && (
          <button
            type="button"
            onClick={clearFile}
            className="text-sm text-primary-blue hover:underline self-start"
          >
            Remove file
          </button>
        )}

        {error && (
          <div className="rounded-xl bg-error-red/10 border border-error-red/30 text-error-red px-4 py-3 text-sm font-urbanist">
            {error}
          </div>
        )}

        {success && (
          <div className="rounded-xl bg-primary-blue/15 border border-primary-blue/40 text-main-text px-4 py-3 text-sm font-urbanist">
            {success}
          </div>
        )}

        <button
          type="submit"
          disabled={!file || uploading}
          className={`
            w-full font-urbanist font-semibold py-3.5 px-6 rounded-2xl transition-all
            ${file && !uploading
              ? 'bg-primary-blue text-white hover:bg-primary-blue/90 shadow-md hover:shadow'
              : 'bg-primary-blue/30 text-primary-blue/70 cursor-not-allowed'}
          `}
        >
          {uploading ? 'Uploading…' : 'Submit'}
        </button>
      </form>

      <div className="mt-10 pt-6 border-t border-primary-blue/20">
        <Link
          to="/"
          className="text-primary-blue hover:underline font-urbanist text-sm"
        >
          ← Back to chatbot
        </Link>
      </div>
    </div>
  );
}

export default IndexPage;
