import React from 'react';
import { useUsersQuery } from '../generated/graphql';

interface Props {

}

export const CameraConfig: React.FC<Props> = () => {

    const {data, } = useUsersQuery({fetchPolicy: 'network-only'});

    if (!data) 
    {
        return <div>loading...</div>
    }

    return (
        <div>
            start camera config
        </div>
    );
}