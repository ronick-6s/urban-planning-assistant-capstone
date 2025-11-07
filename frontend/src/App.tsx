import { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import './ArchitecturalApp.css';

interface Message {
  text: string;
  sender: 'user' | 'assistant';
}

interface SessionInfo {
  session_id: string;
  message_count: number;
  first_message: string;
  last_message: string;
  first_timestamp: string;
  last_timestamp: string;
}

interface UserSessionsResponse {
  user_id: string;
  sessions: SessionInfo[];
  total_sessions: number;
}

const users = [
  { id: 'citizen1', name: 'Urban Resident', avatar: '🏛️', color: '#4a4a4a' },
  { id: 'planner1', name: 'City Planner', avatar: '📐', color: '#2c2c2c' },
  { id: 'admin1', name: 'Administrator', avatar: '🗂️', color: '#1a1a1a' }
];

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [userId, setUserId] = useState('');
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userSessions, setUserSessions] = useState<SessionInfo[]>([]);
  const [selectedSessions, setSelectedSessions] = useState<string[]>([]);
  const [includeAllHistory, setIncludeAllHistory] = useState(false);
  const [loadingSessions, setLoadingSessions] = useState(false);
  const [reportEmail, setReportEmail] = useState('');
  const [showReportDialog, setShowReportDialog] = useState(false);
  const [isGeneratingReport, setIsGeneratingReport] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showSidebar, setShowSidebar] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [userEmail, setUserEmail] = useState('');
  const [showEmailInput, setShowEmailInput] = useState(false);
  const [tempUserId, setTempUserId] = useState(''); // Store selected user ID temporarily
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const currentUser = users.find(u => u.id === userId);

  const switchUser = (newUserId: string) => {
    setTempUserId(newUserId);
    setShowEmailInput(true);
  };

  const handleEmailSubmit = () => {
    if (!userEmail.trim()) {
      alert('Please enter your email address');
      return;
    }
    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(userEmail)) {
      alert('Please enter a valid email address');
      return;
    }
    setUserId(tempUserId);
    setIsLoggedIn(true);
    setMessages([]);
    setShowUserMenu(false);
    setCurrentSessionId(null);
    setShowEmailInput(false);
    // Load user sessions after setting userId
    setTimeout(() => loadUserSessions(tempUserId), 100);
    // Add welcome message
    setTimeout(() => {
      setMessages([{
        text: `Welcome to Urban Planning Studio. Your reports will be saved to your personal folder linked to ${userEmail}. I'm here to help you explore urban development strategies, sustainable city design, and community planning solutions. How can I assist you with your urban planning project today?`,
        sender: 'assistant'
      }]);
    }, 150);
  };

  const startNewChat = () => {
    setMessages([{
      text: `Welcome to Urban Planning Studio. I'm here to help you explore urban development strategies, sustainable city design, and community planning solutions. How can I assist you with your urban planning project today?`,
      sender: 'assistant'
    }]);
    setCurrentSessionId(null); // Clear session ID for new chat
    console.log('Started new chat, cleared session ID');
  };

  const loadUserSessions = async (targetUserId?: string) => {
    const userIdToUse = targetUserId || userId;
    if (!userIdToUse) return;
    
    setLoadingSessions(true);
    try {
      const response = await fetch(`http://127.0.0.1:8000/chat-history/${userIdToUse}`);
      if (response.ok) {
        const data: UserSessionsResponse = await response.json();
        setUserSessions(data.sessions);
      } else {
        console.error('Failed to load user sessions');
      }
    } catch (error) {
      console.error('Error loading user sessions:', error);
    } finally {
      setLoadingSessions(false);
    }
  };

  const loadSessionHistory = async (sessionId: string) => {
    try {
      const response = await fetch(`http://127.0.0.1:8000/session-history/${userId}/${sessionId}`);
      if (response.ok) {
        const data = await response.json();
        const historyLines = data.history.split('\n');
        const sessionMessages: Message[] = [];
        
        for (let i = 0; i < historyLines.length; i++) {
          const line = historyLines[i];
          if (line.startsWith('[USER]')) {
            sessionMessages.push({
              text: line.replace('[USER]', '').trim(),
              sender: 'user'
            });
          } else if (line.startsWith('[ASSISTANT]')) {
            sessionMessages.push({
              text: line.replace('[ASSISTANT]', '').trim(),
              sender: 'assistant'
            });
          }
        }
        
        setMessages(sessionMessages);
        setCurrentSessionId(sessionId); // Set current session ID for follow-up questions
        console.log('Loaded session:', sessionId, 'with', sessionMessages.length, 'messages');
      }
    } catch (error) {
      console.error('Error loading session history:', error);
    }
  };

  const handleSendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = { text: input, sender: 'user' };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const requestBody: any = {
        query: input,
        user_id: userId,
        user_email: userEmail // Include user email for folder management
      };
      
      // Include session ID if we're continuing a previous conversation
      if (currentSessionId) {
        requestBody.session_id = currentSessionId;
        console.log('Continuing session:', currentSessionId);
      } else {
        console.log('Starting new conversation');
      }

      const response = await fetch('http://127.0.0.1:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody),
      });

      if (response.ok) {
        const data = await response.json();
        console.log('Full response received:', data.response);
        console.log('Response length:', data.response.length);
        console.log('Session ID:', data.session_id);
        
        // Set the session ID if not already set (for new conversations)
        if (data.session_id && !currentSessionId) {
          setCurrentSessionId(data.session_id);
          console.log('Set session ID for new conversation:', data.session_id);
        }
        
        const assistantMessage: Message = { text: data.response, sender: 'assistant' };
        setMessages(prev => [...prev, assistantMessage]);
      } else {
        const errorMessage: Message = { 
          text: 'I apologize, but I encountered an error. Please try again.', 
          sender: 'assistant' 
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error('Error:', error);
      const errorMessage: Message = { 
        text: 'Connection error. Please check your network and try again.', 
        sender: 'assistant' 
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateReport = async () => {
    if (messages.length === 0) {
      alert('No conversation to generate report from.');
      return;
    }

    setIsGeneratingReport(true);
    try {
      const response = await fetch('http://127.0.0.1:8000/report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          user_email: userEmail, // Use the user's folder email
          title: "Urban Planning Studio Consultation Report",
          format: "all",
          email: reportEmail.trim() || userEmail, // Use report email or fallback to user email
          include_all_history: includeAllHistory,
          session_ids: selectedSessions.length > 0 ? selectedSessions : undefined
        }),
      });

      if (!response.ok) {
        throw new Error(`Report generation failed: ${response.statusText}`);
      }

      const data = await response.json();
      let successMessage = `✅ Report generated successfully!\n`;
      successMessage += `📄 ${data.reports_generated} report(s) created\n`;
      successMessage += `📁 Formats: ${data.formats?.join(', ')}\n`;
      successMessage += `☁️ Saved to your personal Dropbox folder\n`;
      
      if (data.email_sent) {
        successMessage += `📧 Report sent to: ${data.email_address}`;
      }

      alert(successMessage);
      setShowReportDialog(false);
      setReportEmail('');
      setSelectedSessions([]);
      setIncludeAllHistory(false);
    } catch (error) {
      console.error('Error generating report:', error);
      alert('Failed to generate report. Please try again.');
    } finally {
      setIsGeneratingReport(false);
    }
  };

  if (!isLoggedIn) {
    return (
      <div className="vogue-login">
        <div className="vogue-login-container">
          <h1 className="vogue-title">Urban<br />Planning<br />Studio</h1>
          <p className="vogue-subtitle">We craft intelligent urban solutions that harmonize community needs with sustainable development principles. Our planning approach creates spaces where people thrive, balancing modern infrastructure with environmental stewardship and social equity.</p>
          
          {!showEmailInput ? (
            <div className="vogue-user-grid">
              {users.map((user) => (
                <button
                  key={user.id}
                  onClick={() => switchUser(user.id)}
                  className="vogue-user-card"
                  style={{ '--user-color': user.color } as any}
                >
                  <div className="vogue-user-avatar">{user.avatar}</div>
                  <div className="vogue-user-name">{user.name}</div>
                </button>
              ))}
            </div>
          ) : (
            <div className="vogue-email-form">
              <h3>Enter Your Email</h3>
              <p>Your reports will be saved to a personal Dropbox folder linked to your email address.</p>
              <div className="vogue-form-group">
                <input
                  type="email"
                  value={userEmail}
                  onChange={(e) => setUserEmail(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleEmailSubmit()}
                  placeholder="your.email@domain.com"
                  className="vogue-input"
                  autoFocus
                />
              </div>
              <div className="vogue-form-actions">
                <button 
                  onClick={() => setShowEmailInput(false)}
                  className="vogue-btn vogue-btn--secondary"
                >
                  Back
                </button>
                <button 
                  onClick={() => handleEmailSubmit()}
                  className="vogue-btn vogue-btn--primary"
                  disabled={!userEmail.trim()}
                >
                  Continue
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="vogue-app">
      {/* Header */}
      <header className="vogue-header">
        <div className="vogue-header-left">
          <h1 className="vogue-logo">Urban Planning Studio</h1>
        </div>
        <div className="vogue-header-right">
          <button 
            onClick={() => setShowSidebar(!showSidebar)}
            className="vogue-sessions-btn"
          >
            Previous Sessions
          </button>
          <button 
            onClick={startNewChat}
            className="vogue-new-chat"
          >
            New Chat
          </button>
          <button
            onClick={() => setShowReportDialog(true)}
            className="vogue-report-btn"
            disabled={messages.length === 0}
          >
            Generate Report
          </button>
          <div className="vogue-user-dropdown">
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="vogue-user-trigger"
              style={{ '--user-color': currentUser?.color } as any}
            >
              <span className="vogue-user-avatar-small">{currentUser?.avatar}</span>
              <span className="vogue-user-name-small">{currentUser?.name}</span>
            </button>
            {showUserMenu && (
              <div className="vogue-user-menu">
                {users.map((user) => (
                  <button
                    key={user.id}
                    onClick={() => switchUser(user.id)}
                    className={`vogue-user-menu-item ${user.id === userId ? 'active' : ''}`}
                    style={{ '--user-color': user.color } as any}
                  >
                    <span className="vogue-user-avatar-small">{user.avatar}</span>
                    <span>{user.name}</span>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Sessions Sidebar */}
      {showSidebar && (
        <div className="vogue-sidebar-overlay" onClick={() => setShowSidebar(false)}>
          <div className="vogue-sidebar" onClick={(e) => e.stopPropagation()}>
            <div className="vogue-sidebar-header">
              <h3>Previous Sessions</h3>
              <button 
                onClick={() => setShowSidebar(false)}
                className="vogue-close-btn"
              >
                ✕
              </button>
            </div>
            <div className="vogue-sidebar-content">
              {loadingSessions ? (
                <div className="vogue-loading">
                  <div className="vogue-typing">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                  <p>Loading sessions...</p>
                </div>
              ) : userSessions.length > 0 ? (
                <div className="vogue-sessions-grid">
                  {userSessions.map((session) => (
                    <div 
                      key={session.session_id} 
                      className="vogue-session-card"
                      onClick={() => {
                        loadSessionHistory(session.session_id);
                        setShowSidebar(false);
                      }}
                    >
                      <div className="vogue-session-preview">
                        {session.first_message.substring(0, 80)}...
                      </div>
                      <div className="vogue-session-meta">
                        <span>{session.message_count} messages</span>
                        <span>{new Date(session.last_timestamp).toLocaleDateString()}</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="vogue-empty-state">
                  <p>No previous sessions found.</p>
                  <p>Start a conversation to see your session history here.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Main Chat Area */}
      <main className="vogue-main">
        <div className="vogue-messages">
          {messages.map((msg, index) => (
            <div key={index} className={`vogue-message vogue-message--${msg.sender}`}>
              <div className="vogue-message-content">
                {msg.sender === 'assistant' ? (
                  <div className="vogue-markdown">
                    <ReactMarkdown 
                      remarkPlugins={[remarkGfm]}
                      rehypePlugins={[rehypeHighlight]}
                      components={{
                        table: ({children, ...props}) => (
                          <div className="table-wrapper">
                            <table {...props}>{children}</table>
                          </div>
                        ),
                        thead: ({children, ...props}) => (
                          <thead {...props}>{children}</thead>
                        ),
                        tbody: ({children, ...props}) => (
                          <tbody {...props}>{children}</tbody>
                        ),
                        tr: ({children, ...props}) => (
                          <tr {...props}>{children}</tr>
                        ),
                        th: ({children, ...props}) => (
                          <th {...props}>{children}</th>
                        ),
                        td: ({children, ...props}) => (
                          <td {...props}>{children}</td>
                        ),
                        code: ({children, className, ...props}) => {
                          const match = /language-(\w+)/.exec(className || '');
                          return match ? (
                            <code className={className} {...props}>
                              {children}
                            </code>
                          ) : (
                            <code className="inline-code" {...props}>
                              {children}
                            </code>
                          );
                        },
                        pre: ({children, ...props}) => (
                          <pre {...props}>{children}</pre>
                        ),
                        h1: ({children, ...props}) => (
                          <h1 {...props}>{children}</h1>
                        ),
                        h2: ({children, ...props}) => (
                          <h2 {...props}>{children}</h2>
                        ),
                        h3: ({children, ...props}) => (
                          <h3 {...props}>{children}</h3>
                        ),
                        h4: ({children, ...props}) => (
                          <h4 {...props}>{children}</h4>
                        ),
                        h5: ({children, ...props}) => (
                          <h5 {...props}>{children}</h5>
                        ),
                        h6: ({children, ...props}) => (
                          <h6 {...props}>{children}</h6>
                        ),
                        ul: ({children, ...props}) => (
                          <ul {...props}>{children}</ul>
                        ),
                        ol: ({children, ...props}) => (
                          <ol {...props}>{children}</ol>
                        ),
                        li: ({children, ...props}) => (
                          <li {...props}>{children}</li>
                        ),
                        blockquote: ({children, ...props}) => (
                          <blockquote {...props}>{children}</blockquote>
                        ),
                        p: ({children, ...props}) => (
                          <p {...props}>{children}</p>
                        ),
                        strong: ({children, ...props}) => (
                          <strong {...props}>{children}</strong>
                        ),
                        em: ({children, ...props}) => (
                          <em {...props}>{children}</em>
                        ),
                        a: ({children, href, ...props}) => (
                          <a href={href} target="_blank" rel="noopener noreferrer" {...props}>
                            {children}
                          </a>
                        )
                      }}
                    >
                      {msg.text}
                    </ReactMarkdown>
                  </div>
                ) : (
                  <p>{msg.text}</p>
                )}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="vogue-message vogue-message--assistant">
              <div className="vogue-message-content">
                <div className="vogue-typing">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="vogue-input-area">
          <div className="vogue-input-container">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
              placeholder="Discuss urban development, sustainable planning, community design..."
              className="vogue-input"
            />
            <button 
              onClick={handleSendMessage} 
              className="vogue-send-btn"
              disabled={isLoading || !input.trim()}
            >
              {isLoading ? '⏳' : '→'}
            </button>
          </div>
        </div>
      </main>

      {/* Report Dialog */}
      {showReportDialog && (
        <div className="vogue-modal-overlay" onClick={() => setShowReportDialog(false)}>
          <div className="vogue-modal" onClick={(e) => e.stopPropagation()}>
            <h3 className="vogue-modal-title">Planning Report</h3>
            <p className="vogue-modal-subtitle">Generate a comprehensive urban planning consultation report including development strategies, sustainability recommendations, and community insights from your conversations.</p>
            
            <div className="vogue-form-group">
              <label htmlFor="reportEmail">Email (optional)</label>
              <input
                id="reportEmail"
                type="email"
                value={reportEmail}
                onChange={(e) => setReportEmail(e.target.value)}
                placeholder="Enter email to receive report..."
                className="vogue-input"
              />
            </div>

            <div className="vogue-form-group">
              <label>
                <input
                  type="checkbox"
                  checked={includeAllHistory}
                  onChange={(e) => {
                    setIncludeAllHistory(e.target.checked);
                    if (e.target.checked) setSelectedSessions([]);
                  }}
                />
                Include all conversation history
              </label>
            </div>

            {!includeAllHistory && userSessions.length > 0 && (
              <div className="vogue-form-group">
                <label>Select sessions to include:</label>
                <div className="vogue-sessions-list">
                  {userSessions.map((session) => (
                    <label key={session.session_id} className="vogue-session-item">
                      <input
                        type="checkbox"
                        checked={selectedSessions.includes(session.session_id)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setSelectedSessions([...selectedSessions, session.session_id]);
                          } else {
                            setSelectedSessions(selectedSessions.filter(id => id !== session.session_id));
                          }
                        }}
                      />
                      <div>
                        <div className="vogue-session-preview">
                          {session.first_message.substring(0, 60)}...
                        </div>
                        <div className="vogue-session-meta">
                          {session.message_count} messages • {new Date(session.last_timestamp).toLocaleDateString()}
                        </div>
                      </div>
                    </label>
                  ))}
                </div>
              </div>
            )}
            
            <div className="vogue-modal-actions">
              <button 
                onClick={() => setShowReportDialog(false)}
                className="vogue-btn vogue-btn--secondary"
                disabled={isGeneratingReport}
              >
                Cancel
              </button>
              <button 
                onClick={handleGenerateReport}
                className="vogue-btn vogue-btn--primary"
                disabled={isGeneratingReport}
              >
                {isGeneratingReport ? 'Generating...' : 'Generate Report'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
