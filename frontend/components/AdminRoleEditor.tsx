'use client';

import { useState, useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';
import { adminRoleApi } from '@/lib/api';

interface AdminUser {
    user_id: string;
    role?: any;
}

interface AdminRoleEditorProps {
    adminUser: AdminUser | null;
    onUpdate: () => void;
}

export default function AdminRoleEditor({ adminUser, onUpdate }: AdminRoleEditorProps) {
    const [roleData, setRoleData] = useState<any>(adminUser?.role || {});
    const [newFieldKey, setNewFieldKey] = useState('');
    const [newFieldValue, setNewFieldValue] = useState('');

    useEffect(() => {
        setRoleData(adminUser?.role || {});
    }, [adminUser]);

    const createAdminRoleMutation = useMutation({
        mutationFn: (data: { user_id: string; role: any }) =>
            adminRoleApi.create(data),
        onSuccess: () => onUpdate(),
        onError: (error: any) => {
            const errorMsg = error.response?.data?.detail
                || error.message
                || (typeof error === 'string' ? error : JSON.stringify(error));
            alert(`Error creating admin role: ${errorMsg}`);
            console.error('Create admin role error:', error);
        },
    });

    const patchAdminRoleMutation = useMutation({
        mutationFn: ({ userId, role }: { userId: string; role: any }) =>
            adminRoleApi.patch(userId, role),
        onSuccess: () => onUpdate(),
        onError: (error: any) => {
            const errorMsg = error.response?.data?.detail
                || error.message
                || (typeof error === 'string' ? error : JSON.stringify(error));
            alert(`Error updating admin role: ${errorMsg}`);
            console.error('Update admin role error:', error);
        },
    });

    const handleAddField = () => {
        if (!newFieldKey || !newFieldValue) return;

        const values = newFieldValue.split(',').map((v) => v.trim());
        const updatedRole = {
            ...roleData,
            [newFieldKey]: values,
        };

        setRoleData(updatedRole);
        setNewFieldKey('');
        setNewFieldValue('');
    };

    const handleRemoveField = (key: string) => {
        const updatedRole = { ...roleData };
        delete updatedRole[key];
        setRoleData(updatedRole);
    };

    const handleUpdateFieldValue = (key: string, value: string) => {
        const values = value.split(',').map((v) => v.trim());
        setRoleData({
            ...roleData,
            [key]: values,
        });
    };

    const handleSave = () => {
        if (!adminUser) return;

        if (!adminUser.role) {
            // Create new admin role
            createAdminRoleMutation.mutate({
                user_id: adminUser.user_id,
                role: roleData,
            });
        } else {
            // Patch existing admin role
            patchAdminRoleMutation.mutate({
                userId: adminUser.user_id,
                role: roleData,
            });
        }
    };

    if (!adminUser) {
        return (
            <div className="text-slate-400 text-center py-12">
                Select an admin to edit their roles
            </div>
        );
    }

    return (
        <div className="space-y-4">
            <div className="bg-gradient-to-r from-orange-900/50 to-red-900/50 rounded-lg p-4 border border-orange-700">
                <h3 className="text-white font-semibold mb-2 flex items-center">
                    <span className="mr-2">👑</span>
                    Admin: {adminUser.user_id}
                </h3>
                <p className="text-orange-300 text-sm">Managing admin-level permissions</p>
            </div>

            {/* Existing Fields */}
            <div className="space-y-3">
                {Object.entries(roleData).map(([key, value]) => (
                    <div key={key} className="bg-slate-800/50 rounded-lg p-4 border border-orange-700/50">
                        <div className="flex justify-between items-start mb-2">
                            <label className="text-orange-300 font-medium">{key}</label>
                            <button
                                onClick={() => handleRemoveField(key)}
                                className="text-red-400 hover:text-red-300 text-sm"
                            >
                                Remove
                            </button>
                        </div>
                        <input
                            type="text"
                            value={Array.isArray(value) ? value.join(', ') : String(value)}
                            onChange={(e) => handleUpdateFieldValue(key, e.target.value)}
                            className="w-full px-3 py-2 bg-slate-700 text-white rounded border border-orange-600 focus:border-orange-500 focus:outline-none"
                            placeholder="Comma-separated values"
                        />
                        <p className="text-slate-500 text-xs mt-1">
                            Array: [{Array.isArray(value) ? value.map(v => `"${v}"`).join(', ') : `"${value}"`}]
                        </p>
                    </div>
                ))}
            </div>

            {/* Add New Field */}
            <div className="bg-slate-800/50 rounded-lg p-4 border border-orange-700/50 border-dashed">
                <h4 className="text-white font-medium mb-3">Add New Permission Field</h4>
                <div className="space-y-3">
                    <input
                        type="text"
                        value={newFieldKey}
                        onChange={(e) => setNewFieldKey(e.target.value)}
                        className="w-full px-3 py-2 bg-slate-700 text-white rounded border border-slate-600 focus:border-orange-500 focus:outline-none"
                        placeholder="Field name (e.g., permissions, access_level)"
                    />
                    <input
                        type="text"
                        value={newFieldValue}
                        onChange={(e) => setNewFieldValue(e.target.value)}
                        className="w-full px-3 py-2 bg-slate-700 text-white rounded border border-slate-600 focus:border-orange-500 focus:outline-none"
                        placeholder="Values (comma-separated)"
                    />
                    <button
                        onClick={handleAddField}
                        className="w-full px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded transition-colors"
                    >
                        + Add Field
                    </button>
                </div>
            </div>

            {/* Save Button */}
            <button
                onClick={handleSave}
                disabled={createAdminRoleMutation.isPending || patchAdminRoleMutation.isPending}
                className="w-full px-4 py-3 bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-700 hover:to-red-700 text-white rounded-lg font-semibold transition-colors disabled:opacity-50"
            >
                {createAdminRoleMutation.isPending || patchAdminRoleMutation.isPending
                    ? 'Saving...'
                    : adminUser.role
                        ? 'Update Admin Role'
                        : 'Create Admin Role'}
            </button>

            {/* JSON Preview */}
            <div className="bg-slate-800/50 rounded-lg p-4 border border-orange-700/50">
                <h4 className="text-slate-400 text-sm mb-2">JSON Preview:</h4>
                <pre className="text-slate-300 text-xs overflow-x-auto">
                    {JSON.stringify(roleData, null, 2)}
                </pre>
            </div>
        </div>
    );
}
