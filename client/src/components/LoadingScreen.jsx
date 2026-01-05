import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Loader2 } from 'lucide-react';

const messages = [
    "Website scannen...",
    "Bedrijfsactiviteiten analyseren...",
    "Symbis Praatplaat model toepassen...",
    "Security & Privacy checks uitvoeren...",
    "Rapport opmaken in huisstijl..."
];

export default function LoadingScreen() {
    const [msgIndex, setMsgIndex] = useState(0);

    useEffect(() => {
        const interval = setInterval(() => {
            setMsgIndex((prev) => (prev + 1) % messages.length);
        }, 3000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="card" style={{ textAlign: 'center', padding: '4rem 2rem' }}>
            <motion.div
                animate={{ rotate: 360 }}
                transition={{ repeat: Infinity, duration: 2, ease: "linear" }}
                style={{ display: 'inline-block', marginBottom: '2rem', color: 'var(--color-symbis-accent)' }}
            >
                <Loader2 size={64} />
            </motion.div>

            <motion.h3
                key={msgIndex}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.5 }}
                style={{ fontSize: '1.2rem', fontWeight: 500 }}
            >
                {messages[msgIndex]}
            </motion.h3>

            <p style={{ marginTop: '1rem', color: '#888', fontSize: '0.9rem' }}>
                Dit duurt ongeveer 30 seconden...
            </p>
        </div>
    );
}
