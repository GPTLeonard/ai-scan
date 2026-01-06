import React from 'react';
import { CheckCircle, Mail } from 'lucide-react';
import { motion } from 'framer-motion';

export default function ResultPage({ companyName, email, message }) {

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="card"
            style={{ textAlign: 'center', padding: '4rem 2rem' }}
        >
            <div style={{ color: 'var(--color-symbis-accent)', marginBottom: '1.5rem', display: 'flex', justifyContent: 'center' }}>
                <CheckCircle size={80} />
            </div>

            <h2 style={{ marginBottom: '1rem' }}>Bedankt!</h2>
            <p style={{ fontSize: '1.1rem', color: '#666', marginBottom: '2rem' }}>
                {message || <>We verwerken de AI-scan voor <b>{companyName}</b>.</>}
            </p>

            <p style={{ marginTop: '2rem', fontSize: '0.9rem', color: '#999' }}>
                {email ? (
                    <>
                        <Mail size={16} style={{ marginRight: '6px', verticalAlign: 'text-bottom' }} />
                        We sturen het rapport naar <b>{email}</b>.
                    </>
                ) : (
                    <>Het rapport wordt binnen enkele minuten gemaild.</>
                )}
            </p>
        </motion.div>
    );
}
