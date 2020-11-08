import {Resolver, Query, Mutation, Arg} from 'type-graphql';
import { Camera } from './entity/Camera';


@Resolver()
export class CameraResolver {
    @Query (() => [Camera])
    cameras() {
        return Camera.find();
    }
    
    @Mutation(() => Boolean)
    async addCamera(
        @Arg('cameraID', () => String) cameraID: string,
        @Arg('description', () => String) description: string,
        @Arg('stream', () => String) stream: string,
        @Arg('latitude', () => String) latitude: string,
        @Arg('longitude', () => String) longitude: string,
        
    ) {

        try {
            await Camera.insert({
                cameraID,
                description,
                stream,
                latitude,
                longitude
            });
        } catch (err) {
            console.log(err);
            return false;
        }

        return true;
    }
}