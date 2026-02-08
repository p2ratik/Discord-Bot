'use client';

import { useState } from 'react';

interface AdminUser {
    user_id: string;
    role?: any;
}

interface AdminListProps {
    admins: AdminUser[];
    selectedAdmin: AdminUser | null;
    onSelectAdmin: (admin: AdminUser) => void;
}

export default function AdminList({ admins, selectedAdmin, onSelectAdmin }: AdminListProps) {
    const [newAdminId, setNewAdminId] = useState('');

    const handleAddAdmin = () => {
        if (!newAdminId.trim()) return;

        // Create a new admin object
        const newAdmin: AdminUser = {
            user_id: newAdminId.trim(),
            role: undefined,
        };

        onSelectAdmin(newAdmin);
        setNewAdminId('');
    };

    return (
        <div className="space-y-4">
            {/* Add New Admin */}
            <div className="bg-gradient-to-r from-orange-900/30 to-red-900/30 rounded-lg p-4 border border-orange-700/50">
                <h4 className="text-orange-300 font-medium mb-3">Add New Admin</h4>
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={newAdminId}
                        onChange={(e) => setNewAdminId(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && handleAddAdmin()}
                        className="flex-1 px-3 py-2 bg-slate-700 text-white rounded border border-orange-600 focus:border-orange-500 focus:outline-none"
                        placeholder="Enter admin user ID"
                    />
                    <button
                        onClick={handleAddAdmin}
                        className="px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded transition-colors"
                    >
                        Add
                    </button>
                </div>
            </div>

            {/* Admin List */}
            <div className="space-y-2 max-h-96 overflow-y-auto">
                {admins.length === 0 ? (
                    <div className="text-slate-400 text-center py-8">
                        No admins yet. Add one above.
                    </div>
                ) : (
                    admins.map((admin) => (
                        <button
                            key={admin.user_id}
                            onClick={() => onSelectAdmin(admin)}
                            className={`w-full text-left p-4 rounded-lg border transition-all ${selectedAdmin?.user_id === admin.user_id
                                    ? 'bg-gradient-to-r from-orange-900/50 to-red-900/50 border-orange-500'
                                    : 'bg-slate-800/30 border-slate-700 hover:border-orange-700/50'
                                }`}
                        >
                            <div className="flex items-center justify-between">
                                <div>
                                    <div className="flex items-center">
                                        <span className="mr-2">👑</span>
                                        <span className="text-white font-medium">{admin.user_id}</span>
                                    </div>
                                    <p className="text-slate-400 text-sm mt-1">
                                        {admin.role
                                            ? `${Object.keys(admin.role).length} permission(s)`
                                            : 'No roles assigned'}
                                    </p>
                                </div>
                                {selectedAdmin?.user_id === admin.user_id && (
                                    <div className="text-orange-400">
                                        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                        </svg>
                                    </div>
                                )}
                            </div>
                        </button>
                    ))
                )}
            </div>
        </div>
    );
}
