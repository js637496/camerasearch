import {Entity, PrimaryGeneratedColumn, Column, BaseEntity} from "typeorm";
import { ObjectType, Field, Int } from "type-graphql";

@ObjectType()
@Entity('cameras')
export class Camera extends BaseEntity {
    @Field(() => Int)
    @PrimaryGeneratedColumn()
    id: number;

    @Field()
    @Column("text")
    cameraID: string;

    @Field()
    @Column("text")
    description: string;

    @Field()
    @Column("text")
    stream: string;

    @Field()
    @Column("text")
    latitude: string;

    @Field()
    @Column("text")
    longitude: string;
}