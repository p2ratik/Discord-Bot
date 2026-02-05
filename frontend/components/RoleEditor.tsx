'use client';

import { useState, useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';
import { roleApi } from '@/lib/api';
import { UserWithRoles, RoleData } from '@/lib/types';

interface RoleEditorProps {
    user: UserWithRoles;
    onUpdate: () => void;
}

export default function RoleEditor({ user, onUpdate }: RoleEditorProps) {
    const [roleData, setRoleData] = useState<RoleData>(user.role || {});
    const [newFieldKey, setNewFieldKey] = useState('');
    const [newFieldValue, setNewFieldValue] = useState('');

    useEffect(() => {
        setRoleData(user.role || {});
    }, [user]);

    const createRoleMutation = useMutation({
        mutationFn: (data: { user_id: string; user_name: string; role: any }) =>
            roleApi.create(data),
        onSuccess: () => onUpdate(),
        onError: (error: any) => {
            alert(error.response?.data?.detail || 'Error creating role');
        },
    });

    const patchRoleMutation = useMutation({
        mutationFn: ({ userId, role }: { userId: string; role: any }) =>
            roleApi.patch(userId, role),
        onSuccess: () => onUpdate(),
        onError: (error: any) => {
            alert(error.response?.data?.detail || 'Error updating role');
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
        if (!user.role) {
            // Create new role
            createRoleMutation.mutate({
                user_id: user.user_id,
                user_name: user.username,
                role: roleData,
            });
        } else {
            // Patch existing role
            patchRoleMutation.mutate({
                userId: user.user_id,
                role: roleData,
            });
        }
    };

    return (
        <div className="space-y-4">
            <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
                <h3 className="text-white font-semibold mb-2">{user.username}</h3>
                <p className="text-slate-400 text-sm">ID: {user.user_id}</p>
            </div>

            {/* Existing Fields */}
            <div className="space-y-3">
                {Object.entries(roleData).map(([key, value]) => (
                    <div key={key} className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
                        <div className="flex justify-between items-start mb-2">
                            <label className="text-purple-300 font-medium">{key}</label>
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
                            className="w-full px-3 py-2 bg-slate-700 text-white rounded border border-slate-600 focus:border-purple-500 focus:outline-none"
                            placeholder="Comma-separated values"
                        />
                        <p className="text-slate-500 text-xs mt-1">
                            Array: [{Array.isArray(value) ? value.map(v => `"${v}"`).join(', ') : `"${value}"`}]
                        </p>
                    </div>
                ))}
            </div>

            {/* Add New Field */}
            <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700 border-dashed">
                <h4 className="text-white font-medium mb-3">Add New Field</h4>
                <div className="space-y-3">
                    <input
                        type="text"
                        value={newFieldKey}
                        onChange={(e) => setNewFieldKey(e.target.value)}
                        className="w-full px-3 py-2 bg-slate-700 text-white rounded border border-slate-600 focus:border-purple-500 focus:outline-none"
                        placeholder="Field name (e.g., relation, nicknames)"
                    />
                    <input
                        type="text"
                        value={newFieldValue}
                        onChange={(e) => setNewFieldValue(e.target.value)}
                        className="w-full px-3 py-2 bg-slate-700 text-white rounded border border-slate-600 focus:border-purple-500 focus:outline-none"
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
                disabled={createRoleMutation.isPending || patchRoleMutation.isPending}
                className="w-full px-4 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-semibold transition-colors disabled:opacity-50"
            >
                {createRoleMutation.isPending || patchRoleMutation.isPending
                    ? 'Saving...'
                    : user.role
                        ? 'Update Role'
                        : 'Create Role'}
            </button>

            {/* JSON Preview */}
            <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
                <h4 className="text-slate-400 text-sm mb-2">JSON Preview:</h4>
                <pre className="text-slate-300 text-xs overflow-x-auto">
                    {JSON.stringify(roleData, null, 2)}
                </pre>
            </div>
        </div>
    );
}
