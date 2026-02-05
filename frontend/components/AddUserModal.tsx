'use client';

import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { userApi } from '@/lib/api';

interface AddUserModalProps {
    onClose: () => void;
    onSuccess: () => void;
}

export default function AddUserModal({ onClose, onSuccess }: AddUserModalProps) {
    const [userId, setUserId] = useState('');
    const [username, setUsername] = useState('');

    const createUserMutation = useMutation({
        mutationFn: (data: { user_id: string; username: string }) =>
            userApi.create(data),
        onSuccess: () => {
            onSuccess();
        },
        onError: (error: any) => {
            alert(error.response?.data?.detail || 'Error creating user');
        },
    });

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!userId || !username) {
            alert('Please fill in all fields');
            return;
        }
        createUserMutation.mutate({ user_id: userId, username });
    };

    return (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
            <div className="bg-slate-800 rounded-xl p-6 w-full max-w-md border border-white/20">
                <h2 className="text-2xl font-bold text-white mb-4">Add New User</h2>

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-slate-300 mb-2">User ID</label>
                        <input
                            type="text"
                            value={userId}
                            onChange={(e) => setUserId(e.target.value)}
                            className="w-full px-4 py-2 bg-slate-700 text-white rounded-lg border border-slate-600 focus:border-purple-500 focus:outline-none"
                            placeholder="e.g., user123"
                        />
                    </div>

                    <div>
                        <label className="block text-slate-300 mb-2">Username</label>
                        <input
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            className="w-full px-4 py-2 bg-slate-700 text-white rounded-lg border border-slate-600 focus:border-purple-500 focus:outline-none"
                            placeholder="e.g., John Doe"
                        />
                    </div>

                    <div className="flex gap-3 pt-4">
                        <button
                            type="button"
                            onClick={onClose}
                            className="flex-1 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={createUserMutation.isPending}
                            className="flex-1 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors disabled:opacity-50"
                        >
                            {createUserMutation.isPending ? 'Creating...' : 'Create User'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
