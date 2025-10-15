import type { FC } from 'react';
import {
    Button,
    Card,
    CardContent,
    CardHeader,
    CardTitle,
    Checkbox,
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow
} from '@/components/ui';

type RoleKey = 'admin' | 'manager' | 'user';

type PermissionKey = 'viewAssignments' | 'editAssignments' | 'createUsers' | 'deleteUsers';

type RolePermissions = Record<PermissionKey, boolean>;

const initialData: Record<RoleKey, RolePermissions> = {
    admin: {
        viewAssignments: true,
        editAssignments: true,
        createUsers: true,
        deleteUsers: true
    },
    manager: {
        viewAssignments: true,
        editAssignments: true,
        createUsers: false,
        deleteUsers: false
    },
    user: {
        viewAssignments: true,
        editAssignments: false,
        createUsers: false,
        deleteUsers: false
    }
};

const headers: { key: PermissionKey; label: string }[] = [
    { key: 'viewAssignments', label: 'View Assignments' },
    { key: 'editAssignments', label: 'Edit Assignments' },
    { key: 'createUsers', label: 'Create Users' },
    { key: 'deleteUsers', label: 'Delete Users' }
];

const RolePermissionPage: FC = () => {
    // In a real app this would be in state; using constants here for the static demo
    const data = initialData;

    return (
        <Card>
            <CardHeader>
                <CardTitle>Role Permissions</CardTitle>
            </CardHeader>
            <CardContent className='space-y-4'>
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>Role</TableHead>
                            {headers.map((h) => (
                                <TableHead key={h.key}>{h.label}</TableHead>
                            ))}
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {Object.entries(data).map(([role, perms]) => (
                            <TableRow key={role}>
                                <TableCell className='font-medium capitalize'>{role}</TableCell>
                                {headers.map((h) => (
                                    <TableCell key={h.key}>
                                        <Checkbox checked={perms[h.key]} aria-label={`${role}-${h.key}`} />
                                    </TableCell>
                                ))}
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
                <div className='flex justify-end'>
                    <Button type='button'>Save Changes</Button>
                </div>
            </CardContent>
        </Card>
    );
};

export default RolePermissionPage;

