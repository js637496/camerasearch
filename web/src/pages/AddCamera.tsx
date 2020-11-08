import React, { useState } from 'react'
import { useAddCameraMutation, useCamerasQuery } from '../generated/graphql';
import { RouteComponentProps } from 'react-router-dom';

interface Props {

}

export const AddCamera: React.FC<RouteComponentProps> = ({history}) => {

    const [cameraID, setCameraID] = useState('');
    const [description, setDescription] = useState('');
    const [stream, setStream] = useState('');
    const [latitude, setLatitude] = useState('');
    const [longitude, setLongitude] = useState('');
    const [addCamera] = useAddCameraMutation();

    const {data, } = useCamerasQuery({fetchPolicy: 'network-only'});

    if (!data) 
    {
        return <div>loading...</div>
    }

    return (
        <div>
        <form 
            onSubmit={async e => {
                e.preventDefault()
                console.log('form submitted');
                const response = await addCamera({
                    variables: {
                        cameraID,
                        description,
                        stream,
                        latitude,
                        longitude
                    }
                })

                console.log(response);
                history.push('/');                
            }}
        >
            <div>
                <input 
                    value={cameraID}
                    placeholder="cameraID"
                    onChange={e => {
                        setCameraID(e.target.value);
                    }}
                />
            </div>
            <div>
                <input 
                    value={description}
                    placeholder="description"
                    onChange={e => {
                        setDescription(e.target.value);
                    }}
                />
            </div>
            <div>
                <input 
                    value={stream}
                    placeholder="stream"
                    onChange={e => {
                        setStream(e.target.value);
                    }}
                />
            </div>
            <div>
                <input 
                    value={latitude}
                    placeholder="latitude"
                    onChange={e => {
                        setLatitude(e.target.value);
                    }}
                />
            </div>
            <div>
                <input 
                    value={longitude}
                    placeholder="longitude"
                    onChange={e => {
                        setLongitude(e.target.value);
                    }}
                />
            </div>
            <button type="submit">Add Camera</button>
        </form>
        <ul>
            {data.cameras.map(x => {
                return (
                    <li key={x.id}>
                        {x.cameraID}, {x.description}, {x.stream}
                    </li>
                );
            })}
        </ul>
        </div>
    );
}