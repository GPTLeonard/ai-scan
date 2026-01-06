import React, { useState } from 'react';
import WizardForm from './components/WizardForm';
import LoadingScreen from './components/LoadingScreen';
import ResultPage from './components/ResultPage';

function App() {
  const [view, setView] = useState('form'); // form, loading, result
  const [companyName, setCompanyName] = useState('');
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState(null);

  const handleSubmit = async (data) => {
    setView('loading');
    setCompanyName(data.company_name);
    setEmail(data.email || '');
    setError(null);

    try {
      const payload = {
        company_name: data.company_name ?? '',
        url: data.url ?? '',
        employees: data.employees ?? '',
        industry: data.industry ?? '',
        ai_experience: data.ai_experience ?? '',
        chatgpt_policy: data.chatgpt_policy ?? '',
        use_case_preference: data.use_case_preference ?? '',
        use_case_text: data.use_case_text ?? '',
        email: data.email ?? '',
        name: data.name ?? '',
      };

      // In development, the proxy in vite.config.js will forward /api to localhost:7071
      // In production, Azure Static Web Apps handles this automatically.
      const response = await fetch('/api/generate-report', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || `Error: ${response.statusText}`);
      }

      const result = await response.json();
      setMessage(result.message || 'Bedankt! Je rapport wordt binnen enkele minuten gemaild.');
      setCompanyName(result.company_name || data.company_name);
      setEmail(result.email || data.email || '');
      setView('result');

    } catch (err) {
      console.error(err);
      setError(err.message || 'Er is iets misgegaan bij het genereren.');
      setView('form');
      alert("Er is iets misgegaan. Probeer het opnieuw of controleer de URL.");
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <header style={{ padding: '2rem', textAlign: 'center' }}>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 800, letterSpacing: '-0.02em' }}>SYMBIS | AI SCAN</h1>
      </header>

      <main className="container" style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
        {view === 'form' && <WizardForm onSubmit={handleSubmit} />}
        {view === 'loading' && <LoadingScreen />}
        {view === 'result' && (
          <ResultPage companyName={companyName} email={email} message={message} />
        )}

        {view === 'form' && error && (
          <p style={{ color: 'red', marginTop: '1rem' }}>{error}</p>
        )}
      </main>

      <footer style={{ textAlign: 'center', padding: '2rem', color: '#999', fontSize: '0.8rem' }}>
        &copy; {new Date().getFullYear()} Symbis B.V. - Automation & AI Consult
      </footer>
    </div>
  );
}

export default App;
