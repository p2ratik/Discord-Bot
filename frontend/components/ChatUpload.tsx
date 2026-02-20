'use client';

import { useState, useRef, useCallback } from 'react';
import { chatUploadApi } from '@/lib/api';

type UploadStatus = 'idle' | 'uploading' | 'success' | 'error';

interface UploadResult {
    message: string;
    s3_key: string;
}

export default function ChatUpload() {
    const [file, setFile] = useState<File | null>(null);
    const [status, setStatus] = useState<UploadStatus>('idle');
    const [progress, setProgress] = useState(0);
    const [result, setResult] = useState<UploadResult | null>(null);
    const [errorMsg, setErrorMsg] = useState('');
    const [isDragging, setIsDragging] = useState(false);
    const inputRef = useRef<HTMLInputElement>(null);

    const MAX_SIZE_MB = 10;

    const validateFile = (f: File): string | null => {
        if (!f.name.endsWith('.txt')) return 'Only .txt files are allowed.';
        if (f.size > MAX_SIZE_MB * 1024 * 1024) return `File must be under ${MAX_SIZE_MB} MB.`;
        return null;
    };

    const selectFile = (f: File) => {
        const err = validateFile(f);
        if (err) {
            setErrorMsg(err);
            setFile(null);
            return;
        }
        setErrorMsg('');
        setFile(f);
        setStatus('idle');
        setResult(null);
    };

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        const dropped = e.dataTransfer.files[0];
        if (dropped) selectFile(dropped);
    }, []);

    const handleDragOver = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    }, []);

    const handleDragLeave = useCallback(() => setIsDragging(false), []);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const selected = e.target.files?.[0];
        if (selected) selectFile(selected);
    };

    const handleUpload = async () => {
        if (!file) return;
        setStatus('uploading');
        setProgress(0);
        setErrorMsg('');
        try {
            const res = await chatUploadApi.upload(file, setProgress);
            setResult(res.data);
            setStatus('success');
        } catch (err: any) {
            const msg = err?.response?.data?.detail || 'Upload failed. Please try again.';
            setErrorMsg(msg);
            setStatus('error');
        }
    };

    const reset = () => {
        setFile(null);
        setStatus('idle');
        setProgress(0);
        setResult(null);
        setErrorMsg('');
        if (inputRef.current) inputRef.current.value = '';
    };

    return (
        <div className="max-w-xl mx-auto">
            {/* Drop Zone */}
            <div
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onClick={() => inputRef.current?.click()}
                className={`relative cursor-pointer rounded-2xl border-2 border-dashed p-10 text-center transition-all duration-300 ${isDragging
                        ? 'border-purple-400 bg-purple-500/20 scale-[1.02]'
                        : 'border-white/20 bg-white/5 hover:border-purple-400/50 hover:bg-white/10'
                    }`}
            >
                <input
                    ref={inputRef}
                    type="file"
                    accept=".txt"
                    onChange={handleInputChange}
                    className="hidden"
                />

                <div className="mb-4 text-5xl">📄</div>
                <p className="text-lg font-semibold text-white mb-1">
                    {isDragging ? 'Drop your file here' : 'Drag & drop a .txt file here'}
                </p>
                <p className="text-sm text-slate-400">
                    or click to browse &middot; max {MAX_SIZE_MB} MB
                </p>
            </div>

            {/* Error */}
            {errorMsg && (
                <div className="mt-4 p-3 rounded-lg bg-red-500/20 border border-red-500/40 text-red-300 text-sm flex items-center gap-2">
                    <span>⚠️</span> {errorMsg}
                </div>
            )}

            {/* Selected file info */}
            {file && status !== 'success' && (
                <div className="mt-4 p-4 rounded-xl bg-white/5 border border-white/10 flex items-center justify-between">
                    <div className="flex items-center gap-3 min-w-0">
                        <span className="text-2xl shrink-0">📎</span>
                        <div className="min-w-0">
                            <p className="text-white font-medium truncate">{file.name}</p>
                            <p className="text-slate-400 text-xs">{(file.size / 1024).toFixed(1)} KB</p>
                        </div>
                    </div>
                    <button
                        onClick={(e) => { e.stopPropagation(); reset(); }}
                        className="text-slate-400 hover:text-white transition-colors text-lg px-2"
                        title="Remove file"
                    >
                        ✕
                    </button>
                </div>
            )}

            {/* Progress bar */}
            {status === 'uploading' && (
                <div className="mt-4">
                    <div className="h-2 rounded-full bg-white/10 overflow-hidden">
                        <div
                            className="h-full rounded-full bg-gradient-to-r from-purple-500 to-pink-500 transition-all duration-300"
                            style={{ width: `${progress}%` }}
                        />
                    </div>
                    <p className="text-slate-400 text-xs mt-1 text-right">{progress}%</p>
                </div>
            )}

            {/* Upload button */}
            {file && status !== 'success' && (
                <button
                    onClick={handleUpload}
                    disabled={status === 'uploading'}
                    className={`mt-4 w-full py-3 rounded-xl font-semibold text-white transition-all duration-300 ${status === 'uploading'
                            ? 'bg-purple-600/50 cursor-not-allowed'
                            : 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 shadow-lg shadow-purple-500/30 hover:shadow-purple-500/50'
                        }`}
                >
                    {status === 'uploading' ? 'Uploading…' : '🚀 Upload Chat'}
                </button>
            )}

            {/* Success state */}
            {status === 'success' && result && (
                <div className="mt-4 p-5 rounded-xl bg-emerald-500/10 border border-emerald-500/30">
                    <div className="flex items-center gap-2 mb-3">
                        <span className="text-2xl">✅</span>
                        <p className="text-emerald-300 font-semibold text-lg">{result.message}</p>
                    </div>
                    <div className="p-3 rounded-lg bg-black/30 font-mono text-xs text-slate-300 break-all">
                        <span className="text-slate-500">S3 Key: </span>{result.s3_key}
                    </div>
                    <button
                        onClick={reset}
                        className="mt-4 w-full py-2.5 rounded-xl bg-white/10 hover:bg-white/20 text-white font-medium transition-colors"
                    >
                        Upload Another File
                    </button>
                </div>
            )}
        </div>
    );
}
