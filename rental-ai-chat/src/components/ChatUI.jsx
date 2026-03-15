import { useState, useRef, useEffect } from "react";
import { Send, Upload, LogOut, FileText, Loader2, AlertTriangle, CheckCircle, Info, Plus, Trash2 } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

const API_BASE_URL = "http://localhost:8000/api";

/**
 * ChatUI with User-Level History Persistence
 */
const ChatUI = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: "Hi! 👋 Upload your rental agreement or ask a question to get started.",
    },
  ]);

  const [input, setInput] = useState("");
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [currentDocId, setCurrentDocId] = useState(null);
  const [selectedState, setSelectedState] = useState("NSW");
  const [conversations, setConversations] = useState([]);
  const [loadingConversations, setLoadingConversations] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState(null);

  const fileInputRef = useRef(null);
  const bottomRef = useRef(null);

  const states = ['NSW', 'VIC', 'QLD', 'ACT', 'SA', 'WA', 'TAS', 'NT'];

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Load user conversations on mount
  useEffect(() => {
    if (user?.id) {
      loadUserConversations();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user]);

  // -----------------------------
  // Load All User Conversations
  // -----------------------------
  const loadUserConversations = async () => {
    if (!user?.id) return;
    
    setLoadingConversations(true);
    try {
      const response = await fetch(`${API_BASE_URL}/user/${user.id}/conversations`);
      if (response.ok) {
        const data = await response.json();
        setConversations(data.conversations || []);
      }
    } catch (error) {
      console.error("Failed to load conversations:", error);
    } finally {
      setLoadingConversations(false);
    }
  };

  // -----------------------------
  // Logout Handler
  // -----------------------------
  const handleLogout = () => {
    logout();
    navigate("/");
  };

  // -----------------------------
  // Start New Conversation
  // -----------------------------
  const startNewConversation = () => {
    setMessages([
      {
        role: "assistant",
        content: "Hi! 👋 Upload your rental agreement or ask a question to get started.",
      },
    ]);
    setCurrentDocId(null);
    setFile(null);
  };

  // -----------------------------
  // Load Previous Conversation
  // -----------------------------
  const loadConversation = async (docId) => {
    setCurrentDocId(docId);
    setMessages([
      {
        role: "assistant",
        content: "Loading conversation...",
      },
    ]);

    try {
      const reportResponse = await fetch(`${API_BASE_URL}/report/${docId}`);
      if (reportResponse.ok) {
        const report = await reportResponse.json();
        
        const newMessages = [
          {
            role: "assistant",
            content: `📄 Loaded: ${report.filename}`,
          },
        ];

        if (report.analysis) {
          newMessages.push({
            role: "assistant",
            content: "Here's the analysis for this document:",
            analysis: report.analysis,
          });
        }

        const historyResponse = await fetch(`${API_BASE_URL}/history/${docId}`);
        if (historyResponse.ok) {
          const historyData = await historyResponse.json();
          
          historyData.chats.forEach(chat => {
            newMessages.push(
              {
                role: "user",
                content: chat.prompt,
              },
              {
                role: "assistant",
                content: chat.response,
              }
            );
          });
        }

        setMessages(newMessages);
      }
    } catch (error) {
      console.error("Failed to load conversation:", error);
      setMessages([
        {
          role: "assistant",
          content: "Sorry, I couldn't load that conversation. Please try again.",
        },
      ]);
    }
  };

  // -----------------------------
  // Delete Conversation
  // -----------------------------
  // const deleteConversation = async (docId, e) => {
  //   e.stopPropagation();
  //   setDeleteConfirm(docId);
  // };

  // const confirmDelete = async () => {
  //   const docId = deleteConfirm;
  //   setDeleteConfirm(null);

  //   try {
  //     const response = await fetch(
  //       `${API_BASE_URL}/conversation/${docId}?user_id=${user.id}`,
  //       { method: "DELETE" }
  //     );

  //     if (response.ok) {
  //       loadUserConversations();
        
  //       if (currentDocId === docId) {
  //         startNewConversation();
  //       }
  //     }
  //   } catch (error) {
  //     console.error("Failed to delete conversation:", error);
  //     setMessages((prev) => [
  //       ...prev,
  //       {
  //         role: "assistant",
  //         content: "❌ Failed to delete conversation. Please try again.",
  //       },
  //     ]);
  //   }
  // };




  // -----------------------------
// Delete Conversation (Frontend Only)
// -----------------------------
const deleteConversation = (docId, e) => {
  e.stopPropagation();
  setDeleteConfirm(docId);
};

const confirmDelete = () => {
  const docId = deleteConfirm;
  setDeleteConfirm(null);

  // Remove the conversation from the frontend state
  setConversations((prev) => prev.filter((c) => c.doc_id !== docId));

  // If the currently loaded conversation was deleted, start a new chat
  if (currentDocId === docId) {
    startNewConversation();
  }

  // Optionally, also remove the messages from the chat area
  if (currentDocId === docId) {
    setMessages([
      {
        role: "assistant",
        content: "Hi! 👋 Upload your rental agreement or ask a question to get started.",
      },
    ]);
    setCurrentDocId(null);
  }
};


  // -----------------------------
  // Send Chat Message
  // -----------------------------
  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = {
      role: "user",
      content: input,
    };

    setMessages((prev) => [...prev, userMessage]);
    const userInput = input;
    setInput("");
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          prompt: userInput,
          user_id: user?.id || "default",
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to get response");
      }

      const data = await response.json();

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.response,
        },
      ]);

      loadUserConversations();
    } catch (error) {
      console.error("Chat error:", error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Sorry, I encountered an error. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  // -----------------------------
  // File Upload & Process
  // -----------------------------
  const handleFileChange = async (e) => {
    const uploaded = e.target.files[0];
    if (!uploaded) return;

    setFile(uploaded);
    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        content: `📄 Uploaded: ${uploaded.name}`,
      },
    ]);

    await uploadAndProcess(uploaded);
  };

  const uploadAndProcess = async (fileToUpload) => {
    setUploading(true);
    setMessages((prev) => [
      ...prev,
      {
        role: "assistant",
        content: `Analyzing your contract using ${selectedState} tenancy laws...`,
      },
    ]);

    try {
      const formData = new FormData();
      formData.append("file", fileToUpload);

      const uploadResponse = await fetch(
        `${API_BASE_URL}/upload?state=${selectedState}&user_id=${user.id}`,
        {
          method: "POST",
          body: formData,
        }
      );

      if (!uploadResponse.ok) {
        throw new Error("Upload failed");
      }

      const uploadData = await uploadResponse.json();
      const docId = uploadData.doc_id;
      setCurrentDocId(docId);

      if (uploadData.detected_state && uploadData.detected_state !== selectedState) {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: `⚠️ Note: I detected this is a ${uploadData.detected_state} document, but you selected ${selectedState}. I'll analyze it using ${uploadData.state} laws for accuracy.`,
          },
        ]);
      }

      await fetch(`${API_BASE_URL}/process/${docId}`, {
        method: "POST",
      });

      await pollForReport(docId);
      
      loadUserConversations();

    } catch (error) {
      console.error("Upload/Process error:", error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `❌ Sorry, I encountered an error: ${error.message}`,
        },
      ]);
    } finally {
      setUploading(false);
      setFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  // -----------------------------
  // Poll for Report
  // -----------------------------
  const pollForReport = async (docId, attempts = 0) => {
    if (attempts > 30) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "⚠️ Analysis is taking longer than expected. Please try again.",
        },
      ]);
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/report/${docId}`);
      
      if (response.ok) {
        const report = await response.json();

        if (report.status === "completed" && report.analysis) {
          setMessages((prev) => [
            ...prev,
            {
              role: "assistant",
              content: "✅ Analysis complete! Here's what I found:",
              analysis: report.analysis,
            },
          ]);
          return;
        }
      }

      setTimeout(() => pollForReport(docId, attempts + 1), 2000);
    } catch (error) {
      console.error("Poll error:", error);
      setTimeout(() => pollForReport(docId, attempts + 1), 2000);
    }
  };

  // -----------------------------
  // Enter to Send
  // -----------------------------
  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // -----------------------------
  // Render Analysis Report
  // -----------------------------
  const renderAnalysis = (analysis) => {
    const stats = analysis.statistics || {};
    const issues = analysis.issues_found || [];
    const quickFacts = analysis.quick_facts || {};

    return (
      <div className="space-y-4 mt-4">
        <div className={`rounded-lg p-4 border-2 ${
          analysis.risk_level === 'HIGH' ? 'bg-red-50 border-red-300' :
          analysis.risk_level === 'MEDIUM' ? 'bg-yellow-50 border-yellow-300' :
          'bg-green-50 border-green-300'
        }`}>
          <h3 className="font-bold text-lg mb-2">{analysis.overall_verdict}</h3>
          <p className="text-sm mb-3">{analysis.recommendation}</p>
          <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-semibold ${
            analysis.risk_level === 'HIGH' ? 'bg-red-200 text-red-800' :
            analysis.risk_level === 'MEDIUM' ? 'bg-yellow-200 text-yellow-800' :
            'bg-green-200 text-green-800'
          }`}>
            {analysis.risk_level} RISK
          </div>
        </div>

        {(quickFacts.rent || quickFacts.bond) && (
          <div className="bg-white border rounded-lg p-4">
            <h3 className="font-semibold mb-3 flex items-center gap-2">
              <Info className="w-5 h-5 text-blue-600" />
              Quick Facts
            </h3>
            <div className="grid grid-cols-2 gap-3 text-sm">
              {quickFacts.rent && (
                <div>
                  <div className="text-gray-500">Rent</div>
                  <div className="font-semibold">{quickFacts.rent}</div>
                </div>
              )}
              {quickFacts.bond && (
                <div>
                  <div className="text-gray-500">Bond</div>
                  <div className="font-semibold">{quickFacts.bond}</div>
                </div>
              )}
              {quickFacts.state && (
                <div>
                  <div className="text-gray-500">State</div>
                  <div className="font-semibold">{quickFacts.state}</div>
                </div>
              )}
            </div>
          </div>
        )}

        <div className="grid grid-cols-4 gap-3 text-sm">
          <div className="bg-white rounded-lg p-3 border">
            <div className="text-2xl font-bold text-blue-600">{stats.total_clauses_reviewed || 0}</div>
            <div className="text-xs text-gray-600">Reviewed</div>
          </div>
          <div className="bg-white rounded-lg p-3 border border-red-200">
            <div className="text-2xl font-bold text-red-600">{stats.illegal_clauses || 0}</div>
            <div className="text-xs text-gray-600">Illegal</div>
          </div>
          <div className="bg-white rounded-lg p-3 border border-yellow-200">
            <div className="text-2xl font-bold text-yellow-600">{stats.high_risk_clauses || 0}</div>
            <div className="text-xs text-gray-600">High Risk</div>
          </div>
          <div className="bg-white rounded-lg p-3 border border-orange-200">
            <div className="text-2xl font-bold text-orange-600">{stats.medium_risk_clauses || 0}</div>
            <div className="text-xs text-gray-600">Medium Risk</div>
          </div>
        </div>

        {issues.length > 0 ? (
          <div className="space-y-2">
            <h3 className="font-semibold flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-red-600" />
              Issues Found ({issues.length})
            </h3>
            {issues.map((issue, idx) => (
              <div key={idx} className={`border rounded-lg p-3 ${
                issue.severity === 'HIGH' ? 'bg-red-50 border-red-300' : 'bg-yellow-50 border-yellow-300'
              }`}>
                <div className="flex items-start gap-2">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    issue.severity === 'HIGH' ? 'bg-red-600 text-white' : 'bg-yellow-600 text-white'
                  }`}>
                    {issue.type}
                  </span>
                  <div className="flex-1">
                    <h4 className="font-semibold text-sm mb-1">{issue.title}</h4>
                    <p className="text-sm text-gray-700 mb-2">{issue.description}</p>
                    <p className="text-xs text-gray-600 italic">{issue.why_its_a_problem}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-center gap-2 text-green-800">
              <CheckCircle className="w-5 h-5" />
              <p className="text-sm font-medium">No significant issues found!</p>
            </div>
          </div>
        )}

        {analysis.suggested_questions && analysis.suggested_questions.length > 0 && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 className="font-semibold text-sm mb-2">💬 You can ask me:</h4>
            <div className="flex flex-wrap gap-2">
              {analysis.suggested_questions.map((question, idx) => (
                <button
                  key={idx}
                  onClick={() => setInput(question)}
                  className="text-xs bg-white border border-blue-300 text-blue-700 px-3 py-1 rounded-full hover:bg-blue-100"
                >
                  {question}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Delete Confirmation Modal */}
      {deleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md mx-4">
            <h3 className="text-lg font-bold mb-2">Delete Conversation?</h3>
            <p className="text-gray-600 mb-6">
              This will permanently delete this conversation and all its messages. This action cannot be undone.
            </p>
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => setDeleteConfirm(null)}
                className="px-4 py-2 border rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={confirmDelete}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ---------------- Sidebar ---------------- */}
      <aside className="w-64 bg-white border-r flex flex-col">
        <div className="p-4 border-b">
          <h2 className="font-bold text-lg">Rental Checker</h2>
          <p className="text-sm text-gray-500">{user?.email}</p>
        </div>

        {/* State Selector */}
        <div className="p-4 border-b">
          <label className="block text-xs font-semibold text-gray-500 uppercase mb-2">
            State/Territory
          </label>
          <select
            value={selectedState}
            onChange={(e) => setSelectedState(e.target.value)}
            className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {states.map((state) => (
              <option key={state} value={state}>
                {state}
              </option>
            ))}
          </select>
        </div>

        {/* New Chat Button */}
        <div className="p-4 border-b">
          <button
            onClick={startNewConversation}
            className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium"
          >
            <Plus className="w-4 h-4" />
            New Chat
          </button>
        </div>

        {/* Conversation History */}
        <div className="flex-1 overflow-y-auto">
          <div className="p-4">
            <h3 className="text-xs font-semibold text-gray-500 uppercase mb-3">
              Your Conversations
            </h3>
            
            {loadingConversations ? (
              <div className="flex items-center justify-center py-4">
                <Loader2 className="w-4 h-4 animate-spin text-gray-400" />
              </div>
            ) : conversations.length > 0 ? (
              <div className="space-y-2">
                {conversations.map((conv) => (
                  <div
                    key={conv.doc_id}
                    className={`group relative rounded-lg border hover:bg-gray-50 transition-colors ${
                      currentDocId === conv.doc_id ? 'bg-blue-50 border-blue-300' : 'bg-white'
                    }`}
                  >
                    <button
                      onClick={() => loadConversation(conv.doc_id)}
                      className="w-full text-left p-3"
                    >
                      <div className="flex items-start gap-2">
                        <FileText className="w-4 h-4 mt-0.5 text-gray-400 flex-shrink-0" />
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-gray-900 truncate">
                            {conv.filename}
                          </p>
                          <p className="text-xs text-gray-500 truncate mt-1">
                            {conv.last_message.substring(0, 35)}...
                          </p>
                          <div className="flex items-center gap-2 mt-2">
                            <span className="text-xs text-gray-400">
                              {new Date(conv.last_message_time).toLocaleDateString()}
                            </span>
                            <span className="text-xs text-gray-400">•</span>
                            <span className="text-xs text-gray-400">
                              {conv.message_count} messages
                            </span>
                          </div>
                        </div>
                      </div>
                    </button>
                    
                    {/* Delete button */}
                    <button
                      onClick={(e) => deleteConversation(conv.doc_id, e)}
                      className="absolute top-2 right-2 p-1 rounded opacity-0 group-hover:opacity-100 hover:bg-red-100 transition-opacity"
                      title="Delete conversation"
                    >
                      <Trash2 className="w-3 h-3 text-red-600" />
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500">
                No conversations yet. Upload a document to get started!
              </p>
            )}
          </div>
        </div>

        <button
          onClick={handleLogout}
          className="flex items-center gap-2 p-4 border-t text-red-600 hover:bg-red-50"
        >
          <LogOut className="w-4 h-4" />
          Logout
        </button>
      </aside>

      {/* ---------------- Main Chat ---------------- */}
      <main className="flex-1 flex flex-col">
        {/* Chat messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`max-w-3xl ${
                msg.role === "user"
                  ? "ml-auto text-right"
                  : "mr-auto text-left"
              }`}
            >
              <div
                className={`inline-block px-4 py-3 rounded-xl text-sm ${
                  msg.role === "user"
                    ? "bg-blue-600 text-white"
                    : "bg-white border"
                }`}
              >
                {msg.content}
                {msg.analysis && renderAnalysis(msg.analysis)}
              </div>
            </div>
          ))}

          {(loading || uploading) && (
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <Loader2 className="w-4 h-4 animate-spin" />
              {uploading ? "Analyzing contract..." : "Thinking..."}
            </div>
          )}

          <div ref={bottomRef} />
        </div>

        {/* ---------------- Input Area ---------------- */}
        <div className="border-t bg-white p-4">
          {file && (
            <div className="flex items-center gap-2 text-sm mb-2 text-gray-600">
              <FileText className="w-4 h-4" />
              {file.name}
            </div>
          )}

          <div className="flex items-end gap-2">
            <button
              onClick={() => fileInputRef.current.click()}
              disabled={uploading}
              className="p-2 rounded-lg hover:bg-gray-100 disabled:opacity-50"
            >
              <Upload className="w-5 h-5 text-gray-600" />
            </button>

            <textarea
              rows={1}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={loading}
              placeholder="Ask about your rental agreement..."
              className="flex-1 resize-none border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
            />

            <button
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              className="bg-blue-600 text-white p-2 rounded-lg disabled:opacity-50"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>

          <input
            type="file"
            ref={fileInputRef}
            className="hidden"
            onChange={handleFileChange}
            accept=".pdf,.doc,.docx,.txt"
          />
        </div>
      </main>
    </div>
  );
};

export default ChatUI;