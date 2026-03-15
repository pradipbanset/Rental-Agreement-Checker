// import React, { useState, useRef, useEffect } from 'react';
// import { Upload, Send, FileText, AlertTriangle, CheckCircle, XCircle, Info, ChevronDown, ChevronUp, Loader2, Menu, X, DollarSign, LogOut, User, MessageSquare, Shield, Zap, FileCheck } from 'lucide-react';

// // Authentication Modal Component
// const AuthModal = ({ isOpen, onClose, mode, onAuth }) => {
//   const [email, setEmail] = useState('');
//   const [password, setPassword] = useState('');
//   const [name, setName] = useState('');

//   const handleSubmit = () => {
//     if (email && password && (mode === 'login' || name)) {
//       onAuth({ email, password, name });
//       setEmail('');
//       setPassword('');
//       setName('');
//     }
//   };

//   if (!isOpen) return null;

//   return (
//     <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
//       <div className="bg-white rounded-2xl p-8 max-w-md w-full shadow-2xl">
//         <div className="flex justify-between items-center mb-6">
//           <h2 className="text-2xl font-bold text-gray-900">
//             {mode === 'login' ? 'Welcome back' : 'Create account'}
//           </h2>
//           <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
//             <X className="w-6 h-6" />
//           </button>
//         </div>

//         <div className="space-y-4">
//           {mode === 'signup' && (
//             <div>
//               <label className="block text-sm font-medium text-gray-700 mb-2">Name</label>
//               <input
//                 type="text"
//                 value={name}
//                 onChange={(e) => setName(e.target.value)}
//                 onKeyPress={(e) => e.key === 'Enter' && handleSubmit()}
//                 className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
//                 placeholder="Enter your name"
//               />
//             </div>
//           )}
          
//           <div>
//             <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
//             <input
//               type="email"
//               value={email}
//               onChange={(e) => setEmail(e.target.value)}
//               onKeyPress={(e) => e.key === 'Enter' && handleSubmit()}
//               className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
//               placeholder="you@example.com"
//             />
//           </div>

//           <div>
//             <label className="block text-sm font-medium text-gray-700 mb-2">Password</label>
//             <input
//               type="password"
//               value={password}
//               onChange={(e) => setPassword(e.target.value)}
//               onKeyPress={(e) => e.key === 'Enter' && handleSubmit()}
//               className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
//               placeholder="Enter your password"
//             />
//           </div>

//           <button
//             onClick={handleSubmit}
//             className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
//           >
//             {mode === 'login' ? 'Log in' : 'Sign up'}
//           </button>
//         </div>

//         <div className="mt-6 text-center">
//           <button
//             onClick={() => onClose(mode === 'login' ? 'signup' : 'login')}
//             className="text-sm text-blue-600 hover:text-blue-700"
//           >
//             {mode === 'login' 
//               ? "Don't have an account? Sign up" 
//               : "Already have an account? Log in"}
//           </button>
//         </div>
//       </div>
//     </div>
//   );
// };

// // Homepage Component
// const Homepage = ({ onStartChat, onLogin, onSignup }) => {
//   const features = [
//     {
//       icon: Shield,
//       title: "Legal Protection",
//       description: "Identify unfair clauses that violate tenancy laws"
//     },
//     {
//       icon: FileCheck,
//       title: "Instant Analysis",
//       description: "Get comprehensive contract analysis in seconds"
//     },
//     {
//       icon: Zap,
//       title: "State-Specific",
//       description: "Tailored to your state's rental regulations"
//     },
//     {
//       icon: MessageSquare,
//       title: "Ask Questions",
//       description: "Chat with AI about your rental agreement"
//     }
//   ];

//   return (
//     <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
//       {/* Navigation */}
//       <nav className="border-b border-gray-200 bg-white">
//         <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
//           <div className="flex justify-between items-center h-16">
//             <div className="flex items-center gap-2">
//               <Shield className="w-8 h-8 text-blue-600" />
//               <span className="text-xl font-bold text-gray-900">Rental Checker</span>
//             </div>
            
//             <div className="hidden md:flex items-center gap-8">
//               <a href="#features" className="text-gray-600 hover:text-gray-900">Features</a>
//               <a href="#how-it-works" className="text-gray-600 hover:text-gray-900">How it works</a>
//               <a href="#pricing" className="text-gray-600 hover:text-gray-900">Pricing</a>
//             </div>

//             <div className="flex items-center gap-3">
//               <button
//                 onClick={onLogin}
//                 className="px-4 py-2 text-gray-700 hover:text-gray-900 font-medium"
//               >
//                 Log in
//               </button>
//               <button
//                 onClick={onSignup}
//                 className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
//               >
//                 Sign up for free
//               </button>
//             </div>
//           </div>
//         </div>
//       </nav>

//       {/* Hero Section */}
//       <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-20 text-center">
//         <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
//           Where should we begin?
//         </h1>
//         <p className="text-xl text-gray-600 mb-12">
//           Upload your rental contract and get instant AI-powered analysis for unfair or illegal clauses
//         </p>

//         {/* Main Input Area */}
//         <div className="max-w-2xl mx-auto">
//           <div className="bg-white rounded-2xl shadow-xl border border-gray-200 p-6">
//             <div className="flex items-center gap-4 mb-4">
//               <input
//                 type="text"
//                 placeholder="Ask about rental contracts or upload your agreement..."
//                 className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
//                 onFocus={onStartChat}
//               />
//             </div>
            
//             <div className="flex flex-wrap gap-3 justify-center">
//               <button
//                 onClick={onStartChat}
//                 className="flex items-center gap-2 px-4 py-2 bg-gray-100 rounded-lg hover:bg-gray-200 text-sm font-medium text-gray-700"
//               >
//                 <Upload className="w-4 h-4" />
//                 Upload Contract
//               </button>
//               <button
//                 onClick={onStartChat}
//                 className="flex items-center gap-2 px-4 py-2 bg-gray-100 rounded-lg hover:bg-gray-200 text-sm font-medium text-gray-700"
//               >
//                 <MessageSquare className="w-4 h-4" />
//                 Start Chat
//               </button>
//             </div>
//           </div>

//           <p className="text-sm text-gray-500 mt-4">
//             No account needed • Free analysis • Australian tenancy laws
//           </p>
//         </div>
//       </div>

//       {/* Features Section */}
//       <div id="features" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
//         <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
//           Protect Your Rights as a Tenant
//         </h2>
        
//         <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
//           {features.map((feature, index) => (
//             <div key={index} className="bg-white p-6 rounded-xl border border-gray-200 hover:shadow-lg transition-shadow">
//               <feature.icon className="w-10 h-10 text-blue-600 mb-4" />
//               <h3 className="text-lg font-semibold text-gray-900 mb-2">{feature.title}</h3>
//               <p className="text-gray-600 text-sm">{feature.description}</p>
//             </div>
//           ))}
//         </div>
//       </div>

//       {/* CTA Section */}
//       <div className="bg-blue-600 text-white py-16">
//         <div className="max-w-4xl mx-auto px-4 text-center">
//           <h2 className="text-3xl font-bold mb-4">Ready to check your rental contract?</h2>
//           <p className="text-xl mb-8 text-blue-100">Join thousands of tenants protecting their rights</p>
//           <button
//             onClick={onStartChat}
//             className="px-8 py-4 bg-white text-blue-600 rounded-lg font-semibold hover:bg-blue-50 transition-colors text-lg"
//           >
//             Start Free Analysis
//           </button>
//         </div>
//       </div>

//       {/* Footer */}
//       <footer className="bg-gray-900 text-gray-400 py-8">
//         <div className="max-w-7xl mx-auto px-4 text-center">
//           <p className="text-sm">© 2024 Rental Fairness AU. Protecting tenant rights across Australia.</p>
//         </div>
//       </footer>
//     </div>
//   );
// };

// // Main Rental Checker Component
// const RentalChecker = ({ user, onLogout }) => {
//   const [messages, setMessages] = useState([
//     {
//       id: 1,
//       type: 'assistant',
//       content: "G'day! I'm your Australian Rental Fairness Checker. Upload your rental contract and I'll analyze it for unfair or illegal clauses based on your state's tenancy laws.",
//       timestamp: new Date()
//     }
//   ]);
//   const [input, setInput] = useState('');
//   const [isProcessing, setIsProcessing] = useState(false);
//   const [isChatting, setIsChatting] = useState(false);
//   const [progress, setProgress] = useState(0);
//   const [selectedFile, setSelectedFile] = useState(null);
//   const [currentFileId, setCurrentFileId] = useState(null);
//   const [selectedState, setSelectedState] = useState('NSW');
//   const [sidebarOpen, setSidebarOpen] = useState(false);
//   const [expandedIssues, setExpandedIssues] = useState({});
//   const fileInputRef = useRef(null);
//   const messagesEndRef = useRef(null);
//   const textareaRef = useRef(null);

//   const states = ['NSW', 'VIC', 'QLD', 'ACT', 'SA', 'WA', 'TAS', 'NT'];

//   useEffect(() => {
//     messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
//   }, [messages]);

//   useEffect(() => {
//     if (textareaRef.current) {
//       textareaRef.current.style.height = 'auto';
//       textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 200) + 'px';
//     }
//   }, [input]);

//   const handleFileSelect = (e) => {
//     const file = e.target.files[0];
//     if (file) {
//       setSelectedFile(file);
//       addMessage('user', `Selected file: ${file.name} (${(file.size / 1024).toFixed(2)} KB)`);
//     }
//   };

//   const addMessage = (type, content, data = null) => {
//     const newMessage = {
//       id: Date.now(),
//       type,
//       content,
//       data,
//       timestamp: new Date()
//     };
//     setMessages(prev => [...prev, newMessage]);
//   };

//   const handleUploadAndProcess = async () => {
//     if (!selectedFile) {
//       addMessage('assistant', "Please select a file first. I accept PDF, DOCX, TXT, and image files.");
//       return;
//     }

//     setIsProcessing(true);
//     setProgress(0);
//     addMessage('assistant', `Analyzing your contract using ${selectedState} tenancy laws...`);

//     try {
//       const formData = new FormData();
//       formData.append('file', selectedFile);

//       const uploadResponse = await fetch(`http://localhost:8000/api/upload?state=${selectedState}`, {
//         method: 'POST',
//         body: formData,
//       });

//       if (!uploadResponse.ok) throw new Error('Upload failed');

//       const uploadData = await uploadResponse.json();
//       const fileId = uploadData.doc_id;
      
//       if (!fileId) {
//         throw new Error('No document ID received from server');
//       }
      
//       setCurrentFileId(fileId);
//       if (uploadData.detected_state && uploadData.detected_state !== selectedState) {
//         addMessage('assistant', 
//           `⚠️ Note: I detected this is a ${uploadData.detected_state} document, but you selected ${selectedState}. ` +
//           `I'll analyze it using ${uploadData.state} laws for accuracy.`
//         );
//       }

//       await fetch(`http://localhost:8000/api/process/${fileId}`, {
//         method: 'POST',
//       });

//       let simulatedProgress = 0;
//       const progressInterval = setInterval(() => {
//         simulatedProgress += Math.random() * 10;
//         if (simulatedProgress > 95) simulatedProgress = 95;
//         setProgress(simulatedProgress);
//       }, 500);

//       const pollReport = async () => {
//         try {
//           const res = await fetch(`http://localhost:8000/api/report/${fileId}`);
//           if (res.ok) {
//             const report = await res.json();
            
//             if (report.status === 'completed' && report.analysis) {
//               clearInterval(progressInterval);
//               setProgress(100);
//               addMessage('assistant', '', report.analysis);

//               setSelectedFile(null);
//               if (fileInputRef.current) fileInputRef.current.value = '';
//               setIsProcessing(false);
              
//               setTimeout(() => {
//                 addMessage('assistant', "Analysis complete! Feel free to ask me any questions about your contract.");
//               }, 1000);
//             } else {
//               setTimeout(pollReport, 2000);
//             }
//           } else {
//             setTimeout(pollReport, 2000);
//           }
//         } catch (err) {
//           console.error('Poll error:', err);
//           setTimeout(pollReport, 2000);
//         }
//       };

//       pollReport();

//     } catch (error) {
//       console.error('Upload/Process error:', error);
//       setProgress(0);
//       setIsProcessing(false);
//       addMessage('assistant', `Sorry, I encountered an error: ${error.message}`);
//     }
//   };

//   const handleSendMessage = async () => {
//     if (!input.trim()) return;

//     const userMessage = input.trim();
//     addMessage('user', userMessage);
//     setInput('');

//     if (!currentFileId) {
//       setTimeout(() => {
//         addMessage('assistant', "I'm currently focused on analyzing rental contracts. Please upload a contract file, and I'll check it for unfair or illegal clauses.");
//       }, 500);
//       return;
//     }

//     setIsChatting(true);
    
//     try {
//       const response = await fetch('http://localhost:8000/api/chat', {
//         method: 'POST',
//         headers: {
//           'Content-Type': 'application/json',
//         },
//         body: JSON.stringify({
//           prompt: userMessage,
//         }),
//       });

//       if (!response.ok) throw new Error('Chat request failed');

//       const data = await response.json();
//       addMessage('assistant', data.response);
//     } catch (error) {
//       console.error('Chat error:', error);
//       addMessage('assistant', `Sorry, I encountered an error: ${error.message}`);
//     } finally {
//       setIsChatting(false);
//     }
//   };

//   const handleKeyPress = (e) => {
//     if (e.key === 'Enter' && !e.shiftKey) {
//       e.preventDefault();
//       handleSendMessage();
//     }
//   };

//   const toggleIssue = (index) => {
//     setExpandedIssues(prev => ({
//       ...prev,
//       [index]: !prev[index]
//     }));
//   };

//   const getRiskColor = (riskLevel) => {
//     switch (riskLevel?.toUpperCase()) {
//       case 'HIGH':
//         return 'bg-red-100 text-red-800 border-red-300';
//       case 'MEDIUM':
//         return 'bg-yellow-100 text-yellow-800 border-yellow-300';
//       case 'LOW':
//         return 'bg-green-100 text-green-800 border-green-300';
//       default:
//         return 'bg-gray-100 text-gray-800 border-gray-300';
//     }
//   };

//   const IssueCard = ({ issue, index, expanded, toggleIssue }) => {
//     const isHighSeverity = issue.severity === 'HIGH';
    
//     return (
//       <div className={`border rounded-lg overflow-hidden transition-all ${
//         isHighSeverity ? 'border-red-300 bg-red-50' : 'border-yellow-300 bg-yellow-50'
//       }`}>
//         <div 
//           className="p-4 cursor-pointer hover:bg-opacity-80 transition-colors"
//           onClick={() => toggleIssue(index)}
//         >
//           <div className="flex items-start justify-between gap-3">
//             <div className="flex-1">
//               <div className="flex items-center gap-2 mb-2">
//                 <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${
//                   isHighSeverity ? 'bg-red-600 text-white' : 'bg-yellow-600 text-white'
//                 }`}>
//                   {isHighSeverity ? <XCircle className="w-3 h-3" /> : <AlertTriangle className="w-3 h-3" />}
//                   {issue.type}
//                 </span>
//               </div>
//               <h4 className="font-semibold text-sm mb-1">{issue.title}</h4>
//               <p className="text-sm text-gray-700">{issue.description}</p>
//             </div>
//             {expanded ? <ChevronUp className="w-5 h-5 text-gray-400 flex-shrink-0" /> : <ChevronDown className="w-5 h-5 text-gray-400 flex-shrink-0" />}
//           </div>
//         </div>
        
//         {expanded && (
//           <div className="px-4 pb-4 space-y-3 border-t border-gray-200 pt-3 bg-white">
//             <div>
//               <h5 className="text-xs font-semibold text-gray-500 uppercase mb-1">Why This Is A Problem</h5>
//               <p className="text-sm text-gray-800">{issue.why_its_a_problem}</p>
//             </div>
//             {issue.page_reference && (
//               <div>
//                 <h5 className="text-xs font-semibold text-gray-500 uppercase mb-1">Location</h5>
//                 <p className="text-sm text-gray-600">{issue.page_reference}</p>
//               </div>
//             )}
//           </div>
//         )}
//       </div>
//     );
//   };

//   const renderSmartSummary = (data) => {
//     const summary = data.summary || data;
    
//     if (!summary || typeof summary !== 'object') {
//       return (
//         <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mt-4">
//           <p className="text-sm text-yellow-800">Unable to display report.</p>
//         </div>
//       );
//     }

//     const quickFacts = summary.quick_facts || {};
//     const issues = summary.issues_found || [];
//     const stats = summary.statistics || {};

//     return (
//       <div className="space-y-4 mt-4">
//         <div className={`rounded-lg p-4 border-2 ${
//           summary.risk_level === 'HIGH' ? 'bg-red-50 border-red-300' :
//           summary.risk_level === 'MEDIUM' ? 'bg-yellow-50 border-yellow-300' :
//           'bg-green-50 border-green-300'
//         }`}>
//           <h3 className="font-bold text-lg mb-2">{summary.overall_verdict || 'Analysis Complete'}</h3>
//           <p className="text-sm leading-relaxed mb-3">{summary.recommendation}</p>
          
//           <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-semibold ${getRiskColor(summary.risk_level)}`}>
//             {summary.risk_level === 'HIGH' ? <XCircle className="w-4 h-4" /> :
//              summary.risk_level === 'MEDIUM' ? <AlertTriangle className="w-4 h-4" /> :
//              <CheckCircle className="w-4 h-4" />}
//             {summary.risk_level || 'UNKNOWN'} RISK
//           </div>
//         </div>

//         <div className="bg-white border border-gray-200 rounded-lg p-4">
//           <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
//             <Info className="w-5 h-5 text-blue-600" />
//             Quick Facts
//           </h3>
//           <div className="grid grid-cols-2 gap-3">
//             {quickFacts.rent && (
//               <div className="flex items-center gap-2">
//                 <DollarSign className="w-4 h-4 text-green-600" />
//                 <div>
//                   <div className="text-xs text-gray-500">Rent</div>
//                   <div className="font-semibold">{quickFacts.rent}</div>
//                 </div>
//               </div>
//             )}
//             {quickFacts.bond && (
//               <div className="flex items-center gap-2">
//                 <DollarSign className="w-4 h-4 text-blue-600" />
//                 <div>
//                   <div className="text-xs text-gray-500">Bond</div>
//                   <div className="font-semibold">{quickFacts.bond}</div>
//                 </div>
//               </div>
//             )}
//             {quickFacts.state && (
//               <div>
//                 <div className="text-xs text-gray-500">State</div>
//                 <div className="font-semibold">{quickFacts.state}</div>
//               </div>
//             )}
//             {quickFacts.pages_analyzed > 0 && (
//               <div>
//                 <div className="text-xs text-gray-500">Pages</div>
//                 <div className="font-semibold">{quickFacts.pages_analyzed}</div>
//               </div>
//             )}
//           </div>
//         </div>

//         <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
//           <div className="bg-white rounded-lg p-3 border border-gray-200">
//             <div className="text-2xl font-bold text-blue-600">{stats.total_clauses_reviewed || 0}</div>
//             <div className="text-xs text-gray-600">Reviewed</div>
//           </div>
//           <div className="bg-white rounded-lg p-3 border border-red-200">
//             <div className="text-2xl font-bold text-red-600">{stats.illegal_clauses || 0}</div>
//             <div className="text-xs text-gray-600">Illegal</div>
//           </div>
//           <div className="bg-white rounded-lg p-3 border border-yellow-200">
//             <div className="text-2xl font-bold text-yellow-600">{stats.high_risk_clauses || 0}</div>
//             <div className="text-xs text-gray-600">High Risk</div>
//           </div>
//           <div className="bg-white rounded-lg p-3 border border-orange-200">
//             <div className="text-2xl font-bold text-orange-600">{stats.medium_risk_clauses || 0}</div>
//             <div className="text-xs text-gray-600">Medium Risk</div>
//           </div>
//         </div>

//         {issues.length > 0 ? (
//           <div className="space-y-3">
//             <h3 className="font-semibold text-lg text-gray-800 flex items-center gap-2">
//               <AlertTriangle className="w-5 h-5 text-red-600" />
//               Issues Found ({issues.length})
//             </h3>
//             {issues.map((issue, index) => (
//               <IssueCard 
//                 key={index} 
//                 issue={issue} 
//                 index={index}
//                 expanded={expandedIssues[index]} 
//                 toggleIssue={toggleIssue}
//               />
//             ))}
//           </div>
//         ) : (
//           <div className="bg-green-50 border border-green-200 rounded-lg p-4">
//             <div className="flex items-center gap-2 text-green-800">
//               <CheckCircle className="w-5 h-5" />
//               <p className="text-sm font-medium">No significant issues found!</p>
//             </div>
//           </div>
//         )}

//         {summary.suggested_questions && summary.suggested_questions.length > 0 && (
//           <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
//             <h4 className="font-semibold text-sm text-blue-900 mb-2">💬 You can ask me:</h4>
//             <div className="flex flex-wrap gap-2">
//               {summary.suggested_questions.map((question, idx) => (
//                 <button
//                   key={idx}
//                   onClick={() => setInput(question)}
//                   className="text-xs bg-white border border-blue-300 text-blue-700 px-3 py-1 rounded-full hover:bg-blue-100 transition-colors"
//                 >
//                   {question}
//                 </button>
//               ))}
//             </div>
//           </div>
//         )}
//       </div>
//     );
//   };

//   const renderMessage = (message) => {
//     if (message.type === 'user') {
//       return (
//         <div className="flex justify-end">
//           <div className="bg-blue-600 text-white rounded-2xl px-4 py-3 max-w-[80%] shadow-sm">
//             <p className="text-sm whitespace-pre-wrap">{message.content}</p>
//           </div>
//         </div>
//       );
//     }

//     return (
//       <div className="flex justify-start">
//         <div className="bg-white border border-gray-200 rounded-2xl px-4 py-3 max-w-[90%] shadow-sm">
//           {message.content && <p className="text-sm text-gray-800 whitespace-pre-wrap mb-2">{message.content}</p>}
//           {message.data && renderSmartSummary(message.data)}
//         </div>
//       </div>
//     );
//   };

//   return (
//     <div className="flex h-screen bg-gray-50">
//       <div className={`${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} md:translate-x-0 fixed md:relative z-30 w-64 bg-gray-900 text-white h-full transition-transform duration-300 flex flex-col`}>
//         <div className="p-4 border-b border-gray-700 flex items-center justify-between">
//           <h1 className="text-lg font-bold">Rental Checker</h1>
//           <button onClick={() => setSidebarOpen(false)} className="md:hidden text-gray-400 hover:text-white">
//             <X className="w-5 h-5" />
//           </button>
//         </div>
        
//         <div className="flex-1 overflow-y-auto p-4 space-y-4">
//           {user && (
//             <div className="bg-gray-800 rounded-lg p-3 mb-4">
//               <div className="flex items-center gap-2 mb-2">
//                 <User className="w-4 h-4" />
//                 <span className="text-sm font-medium">{user.name}</span>
//               </div>
//               <button
//                 onClick={onLogout}
//                 className="w-full flex items-center gap-2 text-xs text-gray-400 hover:text-white"
//               >
//                 <LogOut className="w-3 h-3" />
//                 Log out
//               </button>
//             </div>
//           )}

//           <div>
//             <label className="block text-xs font-semibold text-gray-400 uppercase mb-2">State/Territory</label>
//             <select 
//               value={selectedState}
//               onChange={(e) => setSelectedState(e.target.value)}
//               className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
//             >
//               {states.map(state => (
//                 <option key={state} value={state}>{state}</option>
//               ))}
//             </select>
//           </div>

//           <div className="pt-4 border-t border-gray-700">
//             <h3 className="text-xs font-semibold text-gray-400 uppercase mb-2">About</h3>
//             <p className="text-xs text-gray-300 leading-relaxed">
//               This tool analyzes rental contracts against Australian tenancy laws.
//             </p>
//           </div>
//         </div>

//         <div className="p-4 border-t border-gray-700">
//           <p className="text-xs text-gray-500">© 2024 Rental Fairness AU</p>
//         </div>
//       </div>

//       <div className="flex-1 flex flex-col">
//         <div className="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between">
//           <button 
//             onClick={() => setSidebarOpen(true)}
//             className="md:hidden text-gray-600 hover:text-gray-900"
//           >
//             <Menu className="w-6 h-6" />
//           </button>
//           <h2 className="text-lg font-semibold text-gray-800">Australian Rental Fairness Checker</h2>
//           <div className="w-6 md:w-0"></div>
//         </div>

//         <div className="flex-1 overflow-y-auto px-4 py-6 space-y-6">
//           {messages.map(message => (
//             <div key={message.id}>
//               {renderMessage(message)}
//             </div>
//           ))}
//           {isProcessing && (
//             <div className="flex flex-col gap-2">
//               <div className="flex justify-start">
//                 <div className="bg-white border border-gray-200 rounded-2xl px-4 py-3 shadow-sm">
//                   <div className="flex items-center gap-2 text-gray-600">
//                     <Loader2 className="w-4 h-4 animate-spin" />
//                     <span className="text-sm">Analyzing contract...</span>
//                   </div>
//                 </div>
//               </div>
//               <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
//                 <div
//                   className="bg-blue-600 h-2 transition-all"
//                   style={{ width: `${progress}%` }}
//                 />
//               </div>
//               <p className="text-xs text-gray-500">{Math.floor(progress)}% completed</p>
//             </div>
//           )}
//           {isChatting && (
//             <div className="flex justify-start">
//               <div className="bg-white border border-gray-200 rounded-2xl px-4 py-3 shadow-sm">
//                 <div className="flex items-center gap-2 text-gray-600">
//                   <Loader2 className="w-4 h-4 animate-spin" />
//                   <span className="text-sm">Thinking...</span>
//                 </div>
//               </div>
//             </div>
//           )}
//           <div ref={messagesEndRef}></div>
//         </div>

//         <div className="border-t border-gray-200 px-4 py-3 flex items-center gap-3">
//           <input 
//             type="file"
//             ref={fileInputRef}
//             onChange={handleFileSelect}
//             className="hidden"
//           />
//           <button
//             onClick={() => fileInputRef.current?.click()}
//             disabled={isProcessing}
//             className="bg-blue-600 text-white px-3 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2 disabled:opacity-50"
//           >
//             <Upload className="w-4 h-4" />
//             Upload
//           </button>

//           <textarea
//             ref={textareaRef}
//             value={input}
//             onChange={(e) => setInput(e.target.value)}
//             onKeyPress={handleKeyPress}
//             disabled={isChatting}
//             rows={1}
//             placeholder={currentFileId ? "Ask me about your contract..." : "Type a message..."}
//             className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
//           />

//           <button
//             onClick={handleSendMessage}
//             disabled={isChatting || !input.trim()}
//             className="bg-green-600 text-white px-3 py-2 rounded-lg hover:bg-green-700 transition-colors flex items-center disabled:opacity-50"
//           >
//             <Send className="w-4 h-4" />
//           </button>

//           {selectedFile && !isProcessing && (
//             <button
//               onClick={handleUploadAndProcess}
//               disabled={isProcessing}
//               className="bg-indigo-600 text-white px-3 py-2 rounded-lg hover:bg-indigo-700 transition-colors flex items-center disabled:opacity-50"
//             >
//               <FileText className="w-4 h-4" />
//               Process
//             </button>
//           )}
//         </div>
//       </div>
//     </div>
//   );
// };

// // Main App Component
// const App = () => {
//   const [currentView, setCurrentView] = useState('homepage');
//   const [authModalOpen, setAuthModalOpen] = useState(false);
//   const [authMode, setAuthMode] = useState('login');
//   const [user, setUser] = useState(null);

//   const handleAuth = (credentials) => {
//     setUser({
//       name: credentials.name || credentials.email.split('@')[0],
//       email: credentials.email
//     });
//     setAuthModalOpen(false);
//   };

//   const handleLogout = () => {
//     setUser(null);
//     setCurrentView('homepage');
//   };

//   const openAuthModal = (mode) => {
//     setAuthMode(mode);
//     setAuthModalOpen(true);
//   };

//   const closeAuthModal = (switchMode) => {
//     if (switchMode) {
//       setAuthMode(switchMode);
//     } else {
//       setAuthModalOpen(false);
//     }
//   };

//   return (
//     <>
//       {currentView === 'homepage' ? (
//         <Homepage 
//           onStartChat={() => setCurrentView('chat')}
//           onLogin={() => openAuthModal('login')}
//           onSignup={() => openAuthModal('signup')}
//         />
//       ) : (
//         <RentalChecker 
//           user={user}
//           onLogout={handleLogout}
//         />
//       )}

//       <AuthModal 
//         isOpen={authModalOpen}
//         onClose={closeAuthModal}
//         mode={authMode}
//         onAuth={handleAuth}
//       />
//     </>
//   );
// };

// export default App;















// import { useNavigate } from "react-router-dom";
// import { useAuth } from "../context/AuthContext";

// const Home = () => {
//   const navigate = useNavigate();
//   const { user } = useAuth();

//   const startChat = () => {
//     if (user) navigate("/chat");
//     else navigate("/auth");
//   };

//   return (
//     <>
//       {/* your existing homepage UI */}
//       <button onClick={startChat}>Start Free Analysis</button>
//     </>
//   );
// };

// export default Home;






// import { Shield, Upload, MessageSquare } from "lucide-react";
// import { useNavigate } from "react-router-dom";
// import { useAuth } from "../context/AuthContext";

// const Home = () => {
//   const navigate = useNavigate();
//   const { user } = useAuth();

//   const startChat = () => {
//     if (user) navigate("/chat");
//     else navigate("/auth");
//   };

//   return (
//     <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
//       <nav className="border-b bg-white px-6 py-4 flex justify-between">
//         <div className="flex items-center gap-2">
//           <Shield className="w-6 h-6 text-blue-600" />
//           <span className="font-bold text-lg">Rental Checker</span>
//         </div>
//         <button
//           onClick={() => navigate("/auth")}
//           className="text-blue-600 font-medium"
//         >
//           Sign in
//         </button>
//       </nav>

//       <div className="max-w-3xl mx-auto text-center py-24 px-6">
//         <h1 className="text-5xl font-bold mb-6">
//           Check your rental contract in seconds
//         </h1>
//         <p className="text-gray-600 text-xl mb-10">
//           AI-powered analysis based on Australian tenancy laws
//         </p>

//         <div className="flex justify-center gap-4">
//           <button
//             onClick={startChat}
//             className="bg-blue-600 text-white px-6 py-3 rounded-lg flex items-center gap-2"
//           >
//             <Upload className="w-4 h-4" />
//             Upload Contract
//           </button>

//           <button
//             onClick={startChat}
//             className="bg-gray-100 px-6 py-3 rounded-lg flex items-center gap-2"
//           >
//             <MessageSquare className="w-4 h-4" />
//             Start Chat
//           </button>
//         </div>
//       </div>
//     </div>
//   );
// };

// export default Home;









import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Shield } from "lucide-react";

const Home = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  const goToChat = () => {
    if (user) navigate("/chat");
    else navigate("/auth");
  };

  return (
    <div className="min-h-screen bg-white flex flex-col">
      {/* ---------------- Top Bar ---------------- */}
      <header className="flex items-center justify-between px-6 py-4 border-b">
        <div className="flex items-center gap-2 font-semibold">
          <Shield className="w-5 h-5" />
          Rental Checker
        </div>

        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate("/auth")}
            className="text-sm font-medium text-gray-700"
          >
            Log in
          </button>
          <button
            onClick={() => navigate("/auth")}
            className="bg-black text-white text-sm px-4 py-2 rounded-full"
          >
            Sign up for free
          </button>
        </div>
      </header>

      {/* ---------------- Center Content ---------------- */}
      <main className="flex-1 flex flex-col items-center justify-center px-4">
        <h1 className="text-3xl md:text-4xl font-semibold mb-10">
          Ready when you are.
        </h1>

        {/* Prompt Box */}
        <div
          onClick={goToChat}
          className="w-full max-w-2xl border rounded-2xl px-4 py-3 flex items-center justify-between cursor-pointer hover:shadow-md transition"
        >
          <span className="text-gray-500">Ask anything about your rental agreement</span>

          <div className="flex items-center gap-2 text-sm text-gray-400">
            <span className="border px-2 py-1 rounded-md">Enter</span>
          </div>
        </div>

        {/* Helper text */}
        <p className="text-xs text-gray-400 mt-6 text-center max-w-md">
          Upload rental contracts, ask questions, and get AI-powered analysis
          based on Australian tenancy laws.
        </p>
      </main>

      {/* ---------------- Footer ---------------- */}
      <footer className="text-xs text-gray-400 text-center pb-4">
        By using Rental Checker, you agree to our Terms and Privacy Policy.
      </footer>
    </div>
  );
};

export default Home;
