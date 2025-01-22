import React, { useState, useEffect } from "react";
import styled from "styled-components";

interface Kevin {
	id: number;
	name: string;
	wishlist: string[];
	assignedKevin?: Kevin;
}

const Container = styled.div`
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Home Alone Sans', Arial, sans-serif;
`;

const Title = styled.h1`
  color: #c41e3a; // Christmas red
  text-align: center;
`;

const KevinCard = styled.div`
  border: 2px solid #228B22; // Forest green
  border-radius: 8px;
  padding: 15px;
  margin: 10px 0;
  background: #fff;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
`;

const kevins: Kevin[] = [
	{
		id: 1,
		name: "Kevin McCallister",
		wishlist: ["BB Gun", "Pizza", "Micro Machines"],
	},
	{
		id: 2,
		name: "Kevin From Home Alone 2",
		wishlist: ["Hotel Room", "Turtle Doves", "Camera"],
	},
	{
		id: 3,
		name: "Kevin From Work",
		wishlist: ["Coffee Mug", "Stapler", "Post-its"],
	},
	{
		id: 4,
		name: "Evil Kevin",
		wishlist: ["Paint Cans", "Hot Doorknobs", "Tar"],
	},
	{
		id: 5,
		name: "Future Kevin",
		wishlist: ["Hoverboard", "Time Machine", "Robot Butler"],
	},
];

const KevinSecretSanta: React.FC = () => {
	const [assignedKevins, setAssignedKevins] = useState<Kevin[]>([]);
	const [isShuffled, setIsShuffled] = useState(false);

	const shuffleKevins = () => {
		const shuffled = [...kevins];
		for (let i = shuffled.length - 1; i > 0; i--) {
			const j = Math.floor(Math.random() * (i + 1));
			[shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
		}

		// Assign each Kevin to another Kevin
		const assigned = shuffled.map((kevin, index) => ({
			...kevin,
			assignedKevin: shuffled[(index + 1) % shuffled.length],
		}));

		setAssignedKevins(assigned);
		setIsShuffled(true);
	};

	return (
		<Container>
			<Title>🎄 Kevin's Secret Santa Exchange 🎅</Title>

			<button
				onClick={shuffleKevins}
				style={{
					padding: "10px 20px",
					fontSize: "18px",
					backgroundColor: !isShuffled ? "#c41e3a" : "#228B22",
					color: "white",
					border: "none",
					borderRadius: "4px",
					cursor: "pointer",
					display: "block",
					margin: "20px auto",
				}}
			>
				{!isShuffled ? "Assign Secret Kevins!" : "Reassign Kevins!"}
			</button>

			{assignedKevins.map((kevin) => (
				<KevinCard key={kevin.id}>
					<h3>🎁 {kevin.name}</h3>
					<p>
						Will give a gift to: <strong>{kevin.assignedKevin?.name}</strong>
					</p>
					<p>Their wishlist:</p>
					<ul>
						{kevin.assignedKevin?.wishlist.map((item, index) => (
							<li key={index}>{item}</li>
						))}
					</ul>
				</KevinCard>
			))}
		</Container>
	);
};

export default KevinSecretSanta;

// Types for API endpoints
export interface SecretSantaApiResponse {
	success: boolean;
	assignments: {
		giver: Kevin;
		receiver: Kevin;
	}[];
}

// API utility functions
export const fetchKevinAssignments =
	async (): Promise<SecretSantaApiResponse> => {
		// Simulated API call
		return new Promise((resolve) => {
			setTimeout(() => {
				resolve({
					success: true,
					assignments: kevins.map((kevin, index) => ({
						giver: kevin,
						receiver: kevins[(index + 1) % kevins.length],
					})),
				});
			}, 1000);
		});
	};
// A simple React component to display loading state
export class LoadingSpinner extends React.Component {
	render() {
		return (
			<div
				style={{
					display: "flex",
					justifyContent: "center",
					alignItems: "center",
					padding: "20px",
				}}
			>
				<div
					style={{
						width: "50px",
						height: "50px",
						border: "5px solid #f3f3f3",
						borderTop: "5px solid #3498db",
						borderRadius: "50%",
						animation: "spin 1s linear infinite",
					}}
				/>
				<style>
					{`
                        @keyframes spin {
                            0% { transform: rotate(0deg); }
                            100% { transform: rotate(360deg); }
                        }
                    `}
				</style>
			</div>
		);
	}
}
class MyClass {
	constructor() {}
	render() {
		return (
			<div>
				<h1>My Component</h1>
			</div>
		);
	}
}
const handleClick = () => {
    console.log("Button clicked");
};
