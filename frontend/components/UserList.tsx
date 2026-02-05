import { UserWithRoles } from '@/lib/types';

interface UserListProps {
    users: UserWithRoles[];
    selectedUser: UserWithRoles | null;
    onSelectUser: (user: UserWithRoles) => void;
    onDeleteUser: (userId: string) => void;
}

export default function UserList({
    users,
    selectedUser,
    onSelectUser,
    onDeleteUser,
}: UserListProps) {
    return (
        <div className="space-y-2 max-h-[600px] overflow-y-auto">
            {users.length === 0 ? (
                <div className="text-slate-400 text-center py-8">
                    No users yet. Add your first user!
                </div>
            ) : (
                users.map((user) => (
                    <div
                        key={user.user_id}
                        className={`p-4 rounded-lg border transition-all cursor-pointer ${selectedUser?.user_id === user.user_id
                                ? 'bg-purple-600/30 border-purple-400'
                                : 'bg-white/5 border-white/10 hover:bg-white/10'
                            }`}
                        onClick={() => onSelectUser(user)}
                    >
                        <div className="flex justify-between items-start">
                            <div className="flex-1">
                                <h3 className="text-white font-semibold">{user.username}</h3>
                                <p className="text-slate-400 text-sm">ID: {user.user_id}</p>
                                {user.role && (
                                    <div className="mt-2 flex flex-wrap gap-1">
                                        {Object.keys(user.role).map((key) => (
                                            <span
                                                key={key}
                                                className="px-2 py-1 bg-purple-500/20 text-purple-300 text-xs rounded"
                                            >
                                                {key}
                                            </span>
                                        ))}
                                    </div>
                                )}
                            </div>
                            <button
                                onClick={(e) => {
                                    e.stopPropagation();
                                    if (confirm(`Delete user ${user.username}?`)) {
                                        onDeleteUser(user.user_id);
                                    }
                                }}
                                className="ml-2 px-3 py-1 bg-red-600/20 hover:bg-red-600/30 text-red-400 rounded transition-colors text-sm"
                            >
                                Delete
                            </button>
                        </div>
                    </div>
                ))
            )}
        </div>
    );
}
