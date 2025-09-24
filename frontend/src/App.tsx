import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import { QAExample, QAExamplesResponse, QARequest, QAResponse } from './types/api';

const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'http://backend:8000' 
  : 'http://localhost:8000';

const App: React.FC = () => {
  const [qaExamples, setQaExamples] = useState<QAExample[]>([]);
  const [newQuestion, setNewQuestion] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [message, setMessage] = useState<string>('');

    useEffect(() => {
        fetchQAExamples();
    }, []);

  const fetchQAExamples = async (): Promise<void> => {
    try {
      const response = await axios.get<QAExamplesResponse>(`${API_BASE_URL}/api/qa`);
      setQaExamples(response.data.examples);
    } catch (error) {
      console.error('Error fetching QA examples:', error);
      setMessage('Error fetching data from backend');
    }
  };

  const handleSubmitQuestion = async (e: React.FormEvent<HTMLFormElement>): Promise<void> => {
    e.preventDefault();
    if (!newQuestion.trim()) return;

    setLoading(true);
    try {
      const requestData: QARequest = {
        question: newQuestion
      };
      const response = await axios.post<QAResponse>(`${API_BASE_URL}/api/qa`, requestData);
      
      setQaExamples(prev => [...prev, {
        question: response.data.question,
        answer: response.data.answer
      }]);
      
      setNewQuestion('');
      setMessage('Question added successfully!');
    } catch (error) {
      console.error('Error submitting question:', error);
      setMessage('Error submitting question');
    } finally {
      setLoading(false);
    }
  };

    return (
        <div className="App">
            <header className="App-header">
                <h1>QA Bot</h1>
                <p>A full-stack Q&A application with FastAPI and React</p>
            </header>

            <main className="App-main">
                <div className="container">
                    <section className="qa-form">
                        <h2>Add a New Question</h2>
                        <form onSubmit={handleSubmitQuestion}>
                            <div className="form-group">
                <input
                  type="text"
                  value={newQuestion}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setNewQuestion(e.target.value)}
                  placeholder="Enter your question..."
                  className="question-input"
                />
                                <button
                                    type="submit"
                                    disabled={loading || !newQuestion.trim()}
                                    className="submit-btn"
                                >
                                    {loading ? 'Adding...' : 'Add Question'}
                                </button>
                            </div>
                        </form>
                        {message && (
                            <div className={`message ${message.includes('Error') ? 'error' : 'success'}`}>
                                {message}
                            </div>
                        )}
                    </section>

                    <section className="qa-list">
                        <h2>Q&A Examples</h2>
                        {qaExamples.length === 0 ? (
                            <p>No questions yet. Add one above!</p>
                        ) : (
                            <div className="qa-items">
                                {qaExamples.map((qa, index) => (
                                    <div key={index} className="qa-item">
                                        <div className="question">
                                            <strong>Q:</strong> {qa.question}
                                        </div>
                                        <div className="answer">
                                            <strong>A:</strong> {qa.answer}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </section>
                </div>
            </main>
        </div>
    );
}

export default App;
