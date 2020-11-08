import React from 'react';
import { useUsersQuery } from '../generated/graphql';
import ReactHlsPlayer from 'react-hls-player';

interface Props {

}

export const CameraConfig: React.FC<Props> = () => {

    return (
        <div>
            <ReactHlsPlayer
                url='https://s51.nysdot.skyvdn.com:443/rtplive/R2_041/playlist.m3u8'
                autoplay={false}
                controls={true}
                width="100%"
                height="auto"
            />
        </div>
    );
}