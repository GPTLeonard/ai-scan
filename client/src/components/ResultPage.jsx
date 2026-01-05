import React from 'react';
import { CheckCircle, Download } from 'lucide-react';
import { motion } from 'framer-motion';

export default function ResultPage({ pdfBlob, companyName }) {

    const handleDownload = () => {
        if (!pdfBlob) return;
        const url = window.URL.createObjectURL(pdfBlob);
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `Symbis_Scan_${companyName}.pdf`);
        document.body.appendChild(link);
        link.click();
        link.remove();
    };

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

            <h2 style={{ marginBottom: '1rem' }}>Klaar!</h2>
            <p style={{ fontSize: '1.1rem', color: '#666', marginBottom: '2rem' }}>
                De AI-scan voor <b>{companyName}</b> is gereed.
            </p>

            <button onClick={handleDownload} className="btn-primary" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px', margin: '0 auto', fontSize: '1.1rem', padding: '1rem 2rem' }}>
                <Download size={24} />
                Download PDF Rapport
            </button>

            <p style={{ marginTop: '2rem', fontSize: '0.9rem', color: '#999' }}>
                Er is ook een kopie verstuurd naar je email.
            </p>
        </motion.div>
    );
}
