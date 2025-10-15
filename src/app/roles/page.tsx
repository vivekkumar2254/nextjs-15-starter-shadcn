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
    TableRow,
    Tabs,
    TabsContent,
    TabsList,
    TabsTrigger
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

const RolesPage: FC = () => {
    const data = initialData;

    return (
        <Tabs defaultValue='permission'>
            <div className='mb-4 flex items-center justify-between'>
                <TabsList>
                    <TabsTrigger value='permission'>Permission</TabsTrigger>
                    <TabsTrigger value='assignments'>Assignments</TabsTrigger>
                </TabsList>
            </div>
            <TabsContent value='permission'>
                <Card>
                    <CardHeader>
                        <CardTitle>Roles</CardTitle>
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
            </TabsContent>
            <TabsContent value='assignments'>
                <Card>
                    <CardHeader>
                        <CardTitle>Assignments</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <ul className='list-disc space-y-2 pl-6 text-sm text-muted-foreground'>
                            <li>Assignment 1 — placeholder item</li>
                            <li>Assignment 2 — placeholder item</li>
                            <li>Assignment 3 — placeholder item</li>
                        </ul>
                    </CardContent>
                </Card>
            </TabsContent>
        </Tabs>
    );
};

export default RolesPage;

