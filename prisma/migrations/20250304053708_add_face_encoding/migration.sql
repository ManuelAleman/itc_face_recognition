/*
  Warnings:

  - You are about to drop the column `faceId` on the `User` table. All the data in the column will be lost.

*/
-- DropIndex
DROP INDEX "User_faceId_key";

-- AlterTable
ALTER TABLE "User" DROP COLUMN "faceId",
ADD COLUMN     "faceEncoding" DOUBLE PRECISION[];
