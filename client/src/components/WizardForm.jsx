import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, Building, Globe, Users, Briefcase } from 'lucide-react';

export default function WizardForm({ onSubmit }) {
    const [formData, setFormData] = useState({
        company_name: '',
        url: '',
        employees: '1-10',
        industry: 'Zakelijke dienstverlening',
        ai_experience: '3',
        chatgpt_policy: 'Weet ik niet',
        use_case_preference: '',
        use_case_text: '',
        email: '',
        name: ''
    });

    const [step, setStep] = useState(1);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleNext = () => setStep(step + 1);

    const handleSubmit = (e) => {
        e.preventDefault();
        onSubmit(formData);
    };

    const fadeIn = {
        hidden: { opacity: 0, x: 20 },
        visible: { opacity: 1, x: 0 }
    };

    return (
        <div className="card">
            {/* Progress Bar */}
            <div style={{ background: '#eee', height: '6px', borderRadius: '3px', marginBottom: '2rem' }}>
                <div style={{
                    background: 'var(--color-symbis-yellow)',
                    height: '100%',
                    width: `${(step / 4) * 100}%`,
                    borderRadius: '3px',
                    transition: 'width 0.3s ease'
                }} />
            </div>

            <form onSubmit={handleSubmit}>
                {step === 1 && (
                    <motion.div initial="hidden" animate="visible" variants={fadeIn}>
                        <h2>Start jouw AI Scan</h2>
                        <p style={{ marginBottom: '1.5rem', color: '#666' }}>Laten we kennismaken met je bedrijf.</p>

                        <label>Bedrijfsnaam</label>
                        <div className="input-group">
                            <input name="company_name" value={formData.company_name} onChange={handleChange} placeholder="Bijv. Symbis" required />
                        </div>

                        <label>Website URL (Cruciaal voor analyse)</label>
                        <input name="url" value={formData.url} onChange={handleChange} placeholder="https://www.jouwbedrijf.nl" required type="url" />

                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                            <div>
                                <label>Aantal Medewerkers</label>
                                <select name="employees" value={formData.employees} onChange={handleChange}>
                                    <option>1-10</option>
                                    <option>11-50</option>
                                    <option>50-200</option>
                                    <option>200+</option>
                                </select>
                            </div>
                            <div>
                                <label>Branche</label>
                                <select name="industry" value={formData.industry} onChange={handleChange}>
                                    <option>Zakelijke dienstverlening</option>
                                    <option>Zorg</option>
                                    <option>Bouw</option>
                                    <option>Handel</option>
                                    <option>Productie</option>
                                    <option>Anders</option>
                                </select>
                            </div>
                        </div>

                        <button type="button" onClick={handleNext} className="btn-primary" style={{ width: '100%', marginTop: '1rem', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '8px' }}>
                            Volgende Stap <ArrowRight size={18} />
                        </button>
                    </motion.div>
                )}

                {step === 2 && (
                    <motion.div initial="hidden" animate="visible" variants={fadeIn}>
                        <h2>Huidige Situatie</h2>
                        <p style={{ marginBottom: '1.5rem', color: '#666' }}>Waar staan jullie nu?</p>

                        <label>Hoe ervaren is jouw organisatie met AI? (1-10)</label>
                        <input
                            type="range" min="1" max="10"
                            name="ai_experience" value={formData.ai_experience} onChange={handleChange}
                            style={{ width: '100%', accentColor: 'var(--color-symbis-accent)' }}
                        />
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: '#888', marginBottom: '1.5rem' }}>
                            <span>Startpunt (1)</span>
                            <span>In de flow (5)</span>
                            <span>Agents (10)</span>
                        </div>

                        <label>Mag je ChatGPT gebruiken?</label>
                        <select name="chatgpt_policy" value={formData.chatgpt_policy} onChange={handleChange}>
                            <option>Weet ik niet</option>
                            <option>Ja, alles mag</option>
                            <option>Nee, streng verboden</option>
                            <option>Alleen via Copilot (EDP)</option>
                        </select>

                        <button type="button" onClick={handleNext} className="btn-primary" style={{ width: '100%', marginTop: '1rem' }}>
                            Volgende Stap
                        </button>
                        <button type="button" onClick={() => setStep(1)} style={{ background: 'none', border: 'none', color: '#666', width: '100%', marginTop: '1rem', cursor: 'pointer' }}>
                            Terug
                        </button>
                    </motion.div>
                )}

                {step === 3 && (
                    <motion.div initial="hidden" animate="visible" variants={fadeIn}>
                        <h2>Jouw Ideëen</h2>
                        <p style={{ marginBottom: '1.5rem', color: '#666' }}>Heb je al use cases die je met AI wil aanpakken?</p>

                        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginBottom: '1.5rem' }}>
                            <div
                                onClick={() => setFormData({ ...formData, use_case_preference: 'ideas' })}
                                style={{
                                    padding: '1rem',
                                    border: formData.use_case_preference === 'ideas' ? '2px solid var(--color-symbis-accent)' : '1px solid #ddd',
                                    borderRadius: '8px',
                                    background: formData.use_case_preference === 'ideas' ? '#f0f5e5' : 'white',
                                    cursor: 'pointer',
                                    display: 'flex', alignItems: 'center', gap: '10px'
                                }}
                            >
                                <div style={{ background: '#27ae60', color: 'white', borderRadius: '50%', width: '24px', height: '24px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>✓</div>
                                <span>Ja, ik heb concrete ideeën</span>
                            </div>

                            <div
                                onClick={() => setFormData({ ...formData, use_case_preference: 'inspiration' })}
                                style={{
                                    padding: '1rem',
                                    border: formData.use_case_preference === 'inspiration' ? '2px solid var(--color-symbis-accent)' : '1px solid #ddd',
                                    borderRadius: '8px',
                                    background: formData.use_case_preference === 'inspiration' ? '#f0f5e5' : 'white',
                                    cursor: 'pointer',
                                    display: 'flex', alignItems: 'center', gap: '10px'
                                }}
                            >
                                <div style={{ background: '#e74c3c', color: 'white', borderRadius: '50%', width: '24px', height: '24px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>×</div>
                                <span>Nee, ik wil inspiratie</span>
                            </div>
                        </div>

                        {formData.use_case_preference === 'ideas' && (
                            <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }}>
                                <label>Beschrijf kort je use cases:</label>
                                <textarea
                                    name="use_case_text"
                                    value={formData.use_case_text || ''}
                                    onChange={handleChange}
                                    placeholder="Bijv. Ik wil offertes automatisch genereren uit emails..."
                                    rows={4}
                                    style={{ width: '100%', padding: '0.8rem', borderRadius: '4px', border: '1px solid #ddd' }}
                                />
                            </motion.div>
                        )}

                        <button type="button" onClick={handleNext} className="btn-primary" style={{ width: '100%', marginTop: '1rem' }}>
                            Volgende Stap
                        </button>
                        <button type="button" onClick={() => setStep(2)} style={{ background: 'none', border: 'none', color: '#666', width: '100%', marginTop: '1rem', cursor: 'pointer' }}>
                            Terug
                        </button>
                    </motion.div>
                )}

                {step === 4 && (
                    <motion.div initial="hidden" animate="visible" variants={fadeIn}>
                        <h2>Jouw Rapport is bijna klaar</h2>
                        <p style={{ marginBottom: '1.5rem', color: '#666' }}>We sturen het rapport ook naar je mail.</p>

                        <label>Je Naam</label>
                        <input name="name" value={formData.name} onChange={handleChange} placeholder="Voornaam Achternaam" required />

                        <label>Zakelijk E-mailadres</label>
                        <input name="email" value={formData.email} onChange={handleChange} placeholder="naam@bedrijf.nl" required type="email" />

                        <button type="submit" className="btn-primary" style={{ width: '100%', marginTop: '1rem' }}>
                            Start Analyse & Genereer Rapport
                        </button>
                        <button type="button" onClick={() => setStep(3)} style={{ background: 'none', border: 'none', color: '#666', width: '100%', marginTop: '1rem', cursor: 'pointer' }}>
                            Terug
                        </button>
                    </motion.div>
                )}
            </form>
        </div>
    );
}
