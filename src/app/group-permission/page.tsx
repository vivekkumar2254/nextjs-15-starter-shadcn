import type { FC } from 'react';
import {
    Badge,
    Button,
    Card,
    CardContent,
    CardFooter,
    CardHeader,
    CardTitle
} from '@/components/ui';

type Group = {
    id: string;
    name: string;
    description: string;
    status: 'In Progress' | 'Completed' | 'Pending';
};

const groups: Group[] = [
    {
        id: '1',
        name: 'Engineering',
        description: 'Permissions for engineering-related resources and tools.',
        status: 'In Progress'
    },
    {
        id: '2',
        name: 'Operations',
        description: 'Permissions related to deployment and monitoring.',
        status: 'Pending'
    },
    {
        id: '3',
        name: 'Support',
        description: 'Permissions for support desks and user management.',
        status: 'Completed'
    }
];

const getBadgeVariant = (status: Group['status']) => {
    switch (status) {
        case 'Completed':
            return 'secondary' as const;
        case 'In Progress':
            return 'default' as const;
        case 'Pending':
        default:
            return 'outline' as const;
    }
};

const GroupPermissionPage: FC = () => {
    return (
        <div className='grid grid-cols-1 gap-6 sm:grid-cols-2 xl:grid-cols-3'>
            {groups.map((g) => (
                <Card key={g.id} className='flex flex-col'>
                    <CardHeader>
                        <CardTitle>{g.name}</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <p className='text-sm text-muted-foreground'>{g.description}</p>
                    </CardContent>
                    <CardFooter className='mt-auto flex items-center justify-between'>
                        <Badge variant={getBadgeVariant(g.status)}>{g.status}</Badge>
                        <Button size='sm' type='button'>View Details</Button>
                    </CardFooter>
                </Card>
            ))}
        </div>
    );
};

export default GroupPermissionPage;

