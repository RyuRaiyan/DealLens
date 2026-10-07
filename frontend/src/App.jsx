import { useEffect, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);
  const [expandedSource, setExpandedSource] = useState(null);
  const [loading, setLoading] = useState(false);

  const [documents, setDocuments] = useState([]);
  const [selectedDocumentId, setSelectedDocumentId] = useState(null);

  const [currentPage, setCurrentPage] = useState("dashboard");

  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState("");

  // Load documents when the application starts
  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      const response = await fetch(`${API_URL}/documents`);

      if (!response.ok) {
        throw new Error("Failed to load documents");
      }

      const data = await response.json();

      setDocuments(data.documents || []);

      if (data.documents && data.documents.length > 0) {
        setSelectedDocumentId(data.documents[0].document_id);
      }
    } catch (error) {
      console.error("Failed to load documents:", error);
    }
  };

  const askQuestion = async () => {
    if (!question.trim()) return;

    if (!selectedDocumentId) {
      setAnswer("Please upload or select a document first.");
      return;
    }

    setLoading(true);
    setAnswer("");
    setSources([]);

    try {
      const response = await fetch(`${API_URL}/ask`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          document_id: selectedDocumentId,
          question: question,
          top_k: 3,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Something went wrong");
      }

      setAnswer(data.answer);
      setSources(data.sources || []);
    } catch (error) {
      setAnswer(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const uploadPDF = async (event) => {
    const file = event.target.files[0];

    if (!file) return;

    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setUploadMessage("Please select a PDF file.");
      return;
    }

    setUploading(true);
    setUploadMessage("Uploading and processing PDF...");

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(`${API_URL}/upload-pdf`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Upload failed");
      }

      setUploadMessage(
  `Uploaded successfully: ${data.filename}`
);

await loadDocuments();

// Automatically select the newly uploaded document
setSelectedDocumentId(data.document_id);

// Clear the previous document's answer
setAnswer("");
setSources([]);

setCurrentPage("documents");
    } catch (error) {
      setUploadMessage(`Error: ${error.message}`);
    } finally {
      setUploading(false);
      event.target.value = "";
    }
  };

  const selectedDocument = documents.find(
    (doc) => doc.document_id === selectedDocumentId
  );

  return (
    <div className="app">
      {/* SIDEBAR */}
      <aside className="sidebar">
        <div className="logo">
          <div className="logo-mark">D</div>

          <div>
            <h1>DealLens</h1>
            <span>AI Due Diligence</span>
          </div>
        </div>

        <nav>
          <button
            className={`nav-item ${
              currentPage === "dashboard" ? "active" : ""
            }`}
            onClick={() => setCurrentPage("dashboard")}
          >
            <span>⌂</span>
            Dashboard
          </button>

          <button
            className={`nav-item ${
              currentPage === "documents" ? "active" : ""
            }`}
            onClick={() => setCurrentPage("documents")}
          >
            <span>▣</span>
            Documents
          </button>

          <button
            className={`nav-item ${
              currentPage === "analysis" ? "active" : ""
            }`}
            onClick={() => setCurrentPage("analysis")}
          >
            <span>◈</span>
            Analysis
          </button>
        </nav>

        <div className="sidebar-bottom">
          <div className="system-status">
            <span className="status-dot"></span>
            API Connected
          </div>
        </div>
      </aside>

      {/* MAIN CONTENT */}
      <main className="main">

        {/* DASHBOARD */}
        {currentPage === "dashboard" && (
          <>
            <header className="topbar">
              <div>
                <p className="eyebrow">DOCUMENT INTELLIGENCE</p>
                <h2>Due Diligence Workspace</h2>
              </div>

              <div className="api-badge">
                <span className="status-dot"></span>
                System Online
              </div>
            </header>

            <section className="stats">
              <div className="stat-card">
                <span className="stat-label">Documents</span>
                <strong>{documents.length}</strong>
                <small>Available for analysis</small>
              </div>

              <div className="stat-card">
                <span className="stat-label">Indexed Chunks</span>
                <strong>
                  {selectedDocument?.chunks || 0}
                </strong>
                <small>Vectorized knowledge units</small>
              </div>

              <div className="stat-card">
                <span className="stat-label">AI Engine</span>
                <strong>RAG</strong>
                <small>Retrieval augmented generation</small>
              </div>
            </section>

            <section className="workspace">
              <div className="panel question-panel">
                <div className="panel-header">
                  <div>
                    <p className="eyebrow">ASK YOUR DOCUMENT</p>
                    <h3>What would you like to know?</h3>
                  </div>
                </div>

                <textarea
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder="Ask something about the uploaded document..."
                />

                <button
                  className="ask-button"
                  onClick={askQuestion}
                  disabled={
                    loading ||
                    !question.trim() ||
                    !selectedDocumentId
                  }
                >
                  {loading
                    ? "Analyzing..."
                    : "Ask DealLens →"}
                </button>
              </div>

              <div className="panel answer-panel">
                <div className="panel-header">
                  <div>
                    <p className="eyebrow">AI ANALYSIS</p>
                    <h3>Answer</h3>
                  </div>

                  <span className="rag-badge">RAG</span>
                </div>

                <div className="answer-content">
                  {loading ? (
                    <div className="loading">
                      <div className="loader"></div>
                      <p>
                        Searching document and generating answer...
                      </p>
                    </div>
                  ) : answer ? (
                    <>
                      <p style={{ whiteSpace: "pre-line" }}>{answer}</p>

                      {sources.length > 0 && (
  <div className="sources">
    <h4>Sources</h4>

    {sources.map((source, index) => (
      <div className="source-item" key={index}>
        <button
          className="source-button"
          onClick={() =>
            setExpandedSource(
              expandedSource === source.chunk_id
                ? null
                : source.chunk_id
            )
          }
        >
          <span>
            Chunk {source.chunk_index + 1}
            {" · "}
            Similarity: {source.similarity}
          </span>

          <span>
            {expandedSource === source.chunk_id ? "▲" : "▼"}
          </span>
        </button>

        {expandedSource === source.chunk_id && (
          <div className="source-content">
            {source.content}
          </div>
        )}
      </div>
    ))}
  </div>
)}
                    </>
                  ) : (
                    <div className="empty-answer">
                      <div className="empty-icon">✦</div>

                      <p>
                        Your grounded answer will appear here.
                      </p>

                      <span>
                        DealLens retrieves relevant document
                        chunks before generating a response.
                      </span>
                    </div>
                  )}
                </div>
              </div>
            </section>

            <section className="document-section">
              <div className="section-heading">
                <div>
                  <p className="eyebrow">KNOWLEDGE BASE</p>
                  <h3>Current Document</h3>
                </div>

                <span className="document-count">
                  {documents.length} document
                  {documents.length !== 1 ? "s" : ""}
                </span>
              </div>

              {selectedDocument ? (
                <div className="document-card">
                  <div className="document-icon">PDF</div>

                  <div className="document-info">
                    <strong>
                      {selectedDocument.filename}
                    </strong>

                    <span>
                      Document ID:{" "}
                      {selectedDocument.document_id}
                      {" · "}
                      {selectedDocument.chunks} indexed chunks
                    </span>
                  </div>

                  <div className="indexed">
                    <span className="status-dot"></span>
                    Indexed
                  </div>
                </div>
              ) : (
                <div className="document-card">
                  <div className="document-info">
                    <strong>No documents uploaded</strong>

                    <span>
                      Upload a PDF to start analyzing documents.
                    </span>
                  </div>
                </div>
              )}
            </section>
          </>
        )}

        {/* DOCUMENTS PAGE */}
        {currentPage === "documents" && (
          <>
            <header className="topbar">
              <div>
                <p className="eyebrow">KNOWLEDGE BASE</p>
                <h2>Documents</h2>
              </div>

              <div className="api-badge">
                <span className="status-dot"></span>
                System Online
              </div>
            </header>

            <section className="document-section">
              <div className="section-heading">
                <div>
                  <p className="eyebrow">DOCUMENT MANAGEMENT</p>
                  <h3>Upload Documents</h3>
                </div>
              </div>

              <div className="document-card">
                <div className="document-icon">
                  PDF
                </div>

                <div className="document-info">
                  <strong>
                    Upload a company document
                  </strong>

                  <span>
                    PDF files are extracted, chunked and
                    indexed for RAG analysis.
                  </span>
                </div>

                <label className="ask-button upload-button">
                  {uploading
                    ? "Processing..."
                    : "Choose PDF"}

                  <input
                    type="file"
                    accept=".pdf,application/pdf"
                    onChange={uploadPDF}
                    disabled={uploading}
                    hidden
                  />
                </label>
              </div>

              {uploadMessage && (
                <div className="document-card">
                  <div className="document-info">
                    <strong>{uploadMessage}</strong>
                  </div>
                </div>
              )}
            </section>

            <section className="document-section">
              <div className="section-heading">
                <div>
                  <p className="eyebrow">INDEXED DOCUMENTS</p>
                  <h3>Available Documents</h3>
                </div>

                <span className="document-count">
                  {documents.length} document
                  {documents.length !== 1 ? "s" : ""}
                </span>
              </div>

              {documents.map((document) => (
                <div
                  className="document-card"
                  key={document.document_id}
                  onClick={() =>
                    setSelectedDocumentId(
                      document.document_id
                    )
                  }
                >
                  <div className="document-icon">
                    PDF
                  </div>

                  <div className="document-info">
                    <strong>
                      {document.filename}
                    </strong>

                    <span>
                      Document ID:{" "}
                      {document.document_id}
                      {" · "}
                      {document.chunks} indexed chunks
                    </span>
                  </div>

                  <div className="indexed">
                    <span className="status-dot"></span>
                    Indexed
                  </div>
                </div>
              ))}
            </section>
          </>
        )}

        {/* ANALYSIS PAGE */}
        {currentPage === "analysis" && (
          <>
            <header className="topbar">
              <div>
                <p className="eyebrow">AI ANALYSIS</p>
                <h2>Due Diligence Analysis</h2>
              </div>

              <div className="api-badge">
                <span className="status-dot"></span>
                RAG Engine
              </div>
            </header>

            <section className="document-section">
              <div className="section-heading">
                <div>
                  <p className="eyebrow">ANALYSIS ENGINE</p>
                  <h3>Document Intelligence</h3>
                </div>
              </div>

              <div className="document-card">
                <div className="document-icon">
                  AI
                </div>

                <div className="document-info">
                  <strong>
                    RAG-powered document analysis
                  </strong>

                  <span>
                    Ask questions from the Dashboard to
                    retrieve relevant document context and
                    generate grounded answers.
                  </span>
                </div>

                <div className="indexed">
                  <span className="status-dot"></span>
                  Ready
                </div>
              </div>
            </section>
          </>
        )}
      </main>
    </div>
  );
}

export default App;