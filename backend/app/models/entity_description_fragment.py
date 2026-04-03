class EntityDescriptionFragment(Base):
    __tablename__ = "entity_description_fragments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key to the entity this fragment belongs to
    entity_id = Column(UUID(as_uuid=True), ForeignKey("entities.id"), nullable=False, index=True)
    
    # The ID of the source node (e.g., Scene) from the Neo4j graph
    source_node_id = Column(Integer, nullable=False, index=True)
    
    # The actual piece of information
    fragment_text = Column(Text, nullable=False)
    
    # The assessed importance of this fragment (1-10)
    value_score = Column(Integer, max=10, min=1, default=5, nullable=False)

    # Relationship back to the parent Entity
    entity = relationship("Entity", back_populates="description_fragments")